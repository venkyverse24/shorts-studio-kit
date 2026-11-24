r"""setup_tools.py - check, and with your consent install, the tools Shorts Studio Kit uses.

    python tools/setup_tools.py                    # show what is installed and what is missing (changes nothing)
    python tools/setup_tools.py --install          # ask before installing the missing recommended tools
    python tools/setup_tools.py --install --yes    # install the recommended set without asking
    python tools/setup_tools.py --install --with blender    # also install Blender (large, optional)
    python tools/setup_tools.py --install --dry-run          # print the exact commands, run nothing
    python tools/setup_tools.py --json             # machine-readable status
    python tools/setup_tools.py --selftest         # make the installed voice speak and Whisper transcribe it

Options: --target DIR (the studio folder, default: current folder), --only ffmpeg,voice-packages,...

What it can set up (nothing is installed without your yes):
  ffmpeg           joins picture and audio, burns subtitles, checks loudness     (system package manager)
  voice-packages   Pillow, NumPy, SoundFile, kokoro-onnx, faster-whisper         (a venv in <studio>/.shorts-tools)
  kokoro-models    Kokoro voice model files, verified by size and SHA-256        (about 354 MB)
  whisper-model    the Whisper small.en model used for the transcript check      (about 0.5 GB)
  blender          optional, only with --with blender                             (system package manager)
Never installs Claude Code or Python itself, never runs sudo without a terminal to ask for your password,
and never touches your system Python: packages go into the venv inside the studio folder.
After an install it records the paths in <studio>/.shorts-tools/tools.json and fills the EMPTY lines in the
"Tools on this machine" part of brand.md. It never overwrites a line you filled in.
"""
import argparse, glob, hashlib, json, os, platform, re, shutil, subprocess, sys, urllib.request

MB = 1024 * 1024


def detect_os():
    fake = os.environ.get("SHORTS_TOOLS_FAKE_OS")      # test hook: plan commands for another OS
    if fake in ("windows", "mac", "linux"):
        return fake
    return {"Windows": "windows", "Darwin": "mac"}.get(platform.system(), "linux")


OS = detect_os()
FAKE = bool(os.environ.get("SHORTS_TOOLS_FAKE_OS"))
ASSUME_MISSING = {x for x in os.environ.get("SHORTS_TOOLS_ASSUME_MISSING", "").split(",") if x}   # test hook

KOKORO_BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
MODELS = {   # name: (bytes, sha256), checked against the official release
    "kokoro-v1.0.onnx": (325532387, "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5"),
    "voices-v1.0.bin": (28214398, "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"),
}
PY_PACKAGES = ["pillow", "numpy", "soundfile", "kokoro-onnx", "faster-whisper", "av<19"]   # av 19 breaks faster-whisper 1.2.1 (found in a real install test)
WHISPER_MODEL = "small.en"
ORDER = ["ffmpeg", "voice-packages", "kokoro-models", "whisper-model", "blender"]
RECOMMENDED = ["ffmpeg", "voice-packages", "kokoro-models", "whisper-model"]
INFO = {
    "ffmpeg": ("ffmpeg", "joins picture and audio, burns subtitles, checks loudness", "about 100-200 MB", "your package manager (winget, Homebrew or apt)"),
    "voice-packages": ("Python packages: Pillow, NumPy, SoundFile, kokoro-onnx, faster-whisper", "local voice, drawing frames, transcript check", "about 0.4 GB", "PyPI, into a venv in the studio folder"),
    "kokoro-models": ("Kokoro voice model files", "the local text-to-speech voice", "354 MB", "the official kokoro-onnx GitHub release, checked by SHA-256"),
    "whisper-model": ("Whisper small.en model", "transcript check of the final audio", "about 0.5 GB", "Hugging Face, downloaded by faster-whisper"),
    "blender": ("Blender", "3D visuals (optional)", "over 1 GB installed", "your package manager"),
}


def exe(name):
    return name + (".exe" if OS == "windows" else "")


def which_more(name):
    p = shutil.which(name)
    if p:
        return p
    if OS == "windows":
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("ProgramFiles", "C:/Program Files")
        for pat in (os.path.join(local, "Microsoft", "WinGet", "Links", name + ".exe"),
                    os.path.join(local, "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg*", "*", "bin", name + ".exe"),
                    os.path.join(pf, "ffmpeg", "bin", name + ".exe")):
            hits = sorted(glob.glob(pat))
            if hits:
                return hits[-1]
    return None


def venv_python(tools_dir):
    return os.path.join(tools_dir, "venv", "Scripts" if OS == "windows" else "bin", exe("python"))


def models_ok(models_dir):
    return all(os.path.isfile(os.path.join(models_dir, n)) and os.path.getsize(os.path.join(models_dir, n)) == m[0] for n, m in MODELS.items())


def find_blender():
    p = shutil.which("blender")
    if p:
        return p
    pats = {"windows": [os.path.join(os.environ.get("ProgramFiles", "C:/Program Files"), "Blender Foundation", "Blender *", "blender.exe")],
            "mac": ["/Applications/Blender.app/Contents/MacOS/Blender"], "linux": ["/snap/bin/blender", "/usr/bin/blender"]}[OS]
    for pat in pats:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def whisper_cached():
    roots = [os.environ.get("HF_HOME"), os.path.join(os.path.expanduser("~"), ".cache", "huggingface")]
    for r in [x for x in roots if x]:
        if glob.glob(os.path.join(r, "hub", "models--*faster-whisper-" + WHISPER_MODEL)):
            return True
    return False


def detect_all(target):
    tools_dir = os.path.join(os.path.abspath(target), ".shorts-tools")
    vpy = venv_python(tools_dir)
    models_dir = os.path.join(tools_dir, "models")
    ffmpeg, ffprobe = which_more("ffmpeg"), which_more("ffprobe")
    pycmd = next((c for c in ("python", "python3", "py") if shutil.which(c)), None)
    pkgs = False
    if os.path.isfile(vpy):
        pkgs = subprocess.run([vpy, "-c", "import PIL, numpy, soundfile, kokoro_onnx, faster_whisper"], capture_output=True).returncode == 0
    st = {
        "python": dict(ok=sys.version_info >= (3, 10), detail="Python %d.%d.%d (3.10 or newer needed)" % sys.version_info[:3], path=sys.executable, command=pycmd),
        "claude": dict(ok=bool(shutil.which("claude")), detail="Claude Code command", path=shutil.which("claude")),
        "ffmpeg": dict(ok=bool(ffmpeg and ffprobe), detail=ffmpeg or "not found", path=ffmpeg, ffprobe=ffprobe),
        "voice-packages": dict(ok=pkgs, detail=vpy if pkgs else "not set up", path=vpy if pkgs else None),
        "kokoro-models": dict(ok=models_ok(models_dir), detail=models_dir, path=models_dir if models_ok(models_dir) else None),
        "whisper-model": dict(ok=whisper_cached(), detail=WHISPER_MODEL + " in the Hugging Face cache", path=None),
        "blender": dict(ok=bool(find_blender()), detail=find_blender() or "not found", path=find_blender()),
    }
    for k in ASSUME_MISSING:
        if k in st:
            st[k]["ok"] = False
    return st, tools_dir


def have(cmd):
    return FAKE or bool(shutil.which(cmd))


def plan(key, tools_dir, status):
    """Steps for one group. A step is ('cmd', argv) or ('call', description, function) or ('manual', text)."""
    vpy = venv_python(tools_dir)
    if key in ("ffmpeg", "blender"):
        names = {"ffmpeg": ("Gyan.FFmpeg", "ffmpeg", "ffmpeg"), "blender": ("BlenderFoundation.Blender", "blender", "blender")}[key]
        if OS == "windows":
            if have("winget"):
                return [("cmd", ["winget", "install", "--id", names[0], "--exact", "--accept-source-agreements", "--accept-package-agreements"])]
            return [("manual", "winget was not found. Install %s from its official website, then run this again." % key)]
        if OS == "mac":
            if have("brew"):
                return [("cmd", ["brew", "install"] + (["--cask"] if key == "blender" else []) + [names[2]])]
            return [("manual", "Homebrew was not found. Install it from https://brew.sh, then run: brew install %s%s" % ("--cask " if key == "blender" else "", names[2]))]
        if have("apt-get"):
            return [("cmd", ["sudo", "apt-get", "install", "-y", names[2]])]
        if have("dnf"):
            return [("cmd", ["sudo", "dnf", "install", "-y", names[2]])]
        return [("manual", "Install %s with your distribution's package manager, then run this again." % key)]
    if key == "voice-packages":
        steps = []
        if not os.path.isfile(vpy):
            steps.append(("cmd", [sys.executable, "-m", "venv", os.path.join(tools_dir, "venv")]))
        steps.append(("cmd", [vpy, "-m", "pip", "install", "--disable-pip-version-check"] + PY_PACKAGES))
        return steps
    if key == "kokoro-models":
        md = os.path.join(tools_dir, "models")
        return [("call", "download %s (%.0f MB) into %s and verify SHA-256" % (n, m[0] / 1e6, md), (lambda n=n, m=m: download(KOKORO_BASE + n, os.path.join(md, n), m[0], m[1])))
                for n, m in MODELS.items() if not (os.path.isfile(os.path.join(md, n)) and os.path.getsize(os.path.join(md, n)) == m[0])]
    if key == "whisper-model":
        code = "from faster_whisper import WhisperModel; WhisperModel('%s', device='cpu', compute_type='int8')" % WHISPER_MODEL
        return [("cmd", [vpy, "-c", code])]
    return []


def download(url, dest, size, sha):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    h = hashlib.sha256(); got = 0; last = -1
    req = urllib.request.Request(url, headers={"User-Agent": "shorts-studio-kit/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(part, "wb") as f:
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk); h.update(chunk); got += len(chunk)
            pct = got * 100 // size
            if pct // 10 != last:
                last = pct // 10; print("    %s %d%%" % (os.path.basename(dest), min(pct, 100)), flush=True)
    if got != size or h.hexdigest() != sha:
        os.remove(part)
        print("    FAILED: size or SHA-256 does not match the official file. Nothing was kept.")
        return False
    os.replace(part, dest)
    return True


SELFTEST = """
import os, sys, tempfile
from kokoro_onnx import Kokoro
import soundfile as sf
k = Kokoro(sys.argv[1], sys.argv[2])
s, sr = k.create('Testing one two three.', voice='am_michael', speed=1.0, lang='en-us')
p = os.path.join(tempfile.gettempdir(), 'shorts_selftest.wav'); sf.write(p, s, sr)
from faster_whisper import WhisperModel
m = WhisperModel('small.en', device='cpu', compute_type='int8')
segs, _ = m.transcribe(p)
t = ' '.join(x.text.strip() for x in segs)
os.remove(p)
print('    heard: ' + t)
sys.exit(0 if t.strip() else 1)
"""


def selftest(tools_dir):
    """Make the installed voice say a sentence and have Whisper transcribe it. Catches version breakage that imports do not."""
    md = os.path.join(tools_dir, "models")
    print("\nSelf-test: the voice speaks a sentence and Whisper transcribes it (about 20 seconds)...")
    r = subprocess.run([venv_python(tools_dir), "-c", SELFTEST, os.path.join(md, "kokoro-v1.0.onnx"), os.path.join(md, "voices-v1.0.bin")], capture_output=True, text=True)
    if r.returncode == 0:
        print(r.stdout.rstrip()); print("  voice stack works"); return True
    print("  SELF-TEST FAILED. Last lines of the error:")
    for line in (r.stderr or r.stdout).strip().splitlines()[-4:]:
        print("    " + line)
    print("  The tools are installed but something does not work together. Please report this with the lines above.")
    return False


def run_step(step, dry):
    kind = step[0]
    if kind == "manual":
        print("    MANUAL: " + step[1]); return False
    if kind == "cmd":
        argv = step[1]
        print("    $ " + " ".join(('"%s"' % x) if any(c in x for c in ' <>|&') else x for x in argv))
        if dry:
            return True
        if argv[0] == "sudo" and not sys.stdin.isatty():
            print("    needs sudo and a terminal for your password: run the line above yourself."); return False
        return subprocess.run(argv).returncode == 0
    print("    " + step[1])
    return True if dry else bool(step[2]())


def ask(question, yes):
    if yes:
        return True
    try:
        return input(question + " [y/N] ").strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print(); return False


def write_config(target, tools_dir, st):
    os.makedirs(tools_dir, exist_ok=True)
    md = os.path.join(tools_dir, "models")
    cfg = {"python": st["python"]["command"], "venv_python": st["voice-packages"]["path"], "ffmpeg": st["ffmpeg"]["path"], "ffprobe": st["ffmpeg"].get("ffprobe"),
           "kokoro_model": os.path.join(md, "kokoro-v1.0.onnx") if st["kokoro-models"]["ok"] else None,
           "kokoro_voices": os.path.join(md, "voices-v1.0.bin") if st["kokoro-models"]["ok"] else None,
           "whisper_model": WHISPER_MODEL if st["whisper-model"]["ok"] else None, "blender": st["blender"]["path"]}
    json.dump(cfg, open(os.path.join(tools_dir, "tools.json"), "w", encoding="utf-8"), indent=2)
    return cfg


def fill_brand(brand_path, cfg):
    """Fill only EMPTY 'Tools on this machine' lines. Returns the labels that were filled."""
    if not os.path.isfile(brand_path):
        return []
    values = {
        "- Renderer for visuals": ("Blender at " + cfg["blender"]) if cfg.get("blender") else ("simple animated frames drawn with Python (Pillow) and encoded with ffmpeg" if cfg.get("venv_python") else None),
        "- Narration tool and command": ("Kokoro, local, voice am_michael. Python: %s . Model files: %s and %s" % (cfg["venv_python"], cfg["kokoro_model"], cfg["kokoro_voices"])) if cfg.get("venv_python") and cfg.get("kokoro_model") else None,
        "- ffmpeg path": (cfg["ffmpeg"] + (" (ffprobe: %s)" % cfg["ffprobe"] if cfg.get("ffprobe") else "")) if cfg.get("ffmpeg") else None,
        "- Python command": cfg.get("python"),
    }
    lines = open(brand_path, encoding="utf-8").read().split("\n")
    filled = []
    for i, line in enumerate(lines):
        for label, val in values.items():
            if val and line.startswith(label) and line.rstrip().endswith(":"):
                lines[i] = line.rstrip() + " " + val
                filled.append(label[2:])
    if filled:
        open(brand_path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    return filled


def show(st):
    print("\nTools Shorts Studio Kit uses:")
    rows = [("python", "Python 3.10+ (required, not installed by this tool)"), ("claude", "Claude Code (required, not installed by this tool)")]
    rows += [(k, INFO[k][0] + "  [" + INFO[k][2] + "]") for k in ORDER]
    for k, label in rows:
        print("  %-9s %s" % ("[ok]" if st[k]["ok"] else "[missing]", label))
    print("  Blender is optional. Earshot (sound effects) is optional and never installed by this tool: see the shorts-earshot skill.")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--target", default=os.getcwd())
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--with", dest="extra", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--installer-mode", action="store_true")
    a = ap.parse_args()
    target = os.path.abspath(a.target)
    if a.installer_mode and os.environ.get("KIT_INSTALL_TOOLS", "").lower() == "no":
        return                                   # the user asked to skip the check
    st, tools_dir = detect_all(target)

    if a.json:
        print(json.dumps(st, indent=2)); return
    show(st)

    if a.selftest:
        sys.exit(0 if (st["voice-packages"]["ok"] and st["kokoro-models"]["ok"] and st["whisper-model"]["ok"] and selftest(tools_dir)) else 1)

    if a.installer_mode:
        choice = os.environ.get("KIT_INSTALL_TOOLS", "").lower()
        missing = [k for k in RECOMMENDED if not st[k]["ok"]]
        if choice == "no" or not missing:
            return
        print("\nMissing recommended tools:")
        for k in missing:
            print("  - %s: %s. Size: %s. From %s." % (INFO[k][0], INFO[k][1], INFO[k][2], INFO[k][3]))
        if choice == "yes":
            a.install, a.yes = True, True
        elif sys.stdin.isatty() and ask("\nInstall these now? Nothing is installed without your yes.", False):
            a.install, a.yes = True, True
        else:
            print("\nSkipped. To install later, run:  python tools/setup_tools.py --install")
            return

    if not a.install:
        print("\nNothing changed. To install the missing tools:  python tools/setup_tools.py --install")
        return

    want = [k for k in RECOMMENDED if not st[k]["ok"]] + [k.strip() for k in a.extra.split(",") if k.strip() and not st.get(k.strip(), {}).get("ok")]
    if a.only:
        only = {k.strip() for k in a.only.split(",")}
        want = [k for k in ORDER if k in only and not st[k]["ok"]]
    want = [k for k in ORDER if k in want]
    if not want:
        print("\nEverything requested is already installed."); return
    if not st["python"]["ok"]:
        print("\nPython 3.10 or newer is needed for the voice packages. Install it first (for example: winget install Python.Python.3.12), then run this again.")
        want = [k for k in want if k not in ("voice-packages", "whisper-model")]

    results = {}
    for key in want:
        title, why, size, source = INFO[key]
        print("\n== %s: %s. Size: %s. From %s." % (title, why, size, source))
        if key == "whisper-model" and not (st["voice-packages"]["ok"] or results.get("voice-packages") or "voice-packages" in want):
            print("    needs the voice packages first. Skipped."); continue
        if not a.dry_run and not ask("Install %s?" % title, a.yes):
            print("    skipped"); continue
        ok = True
        for step in plan(key, tools_dir, st):
            ok = run_step(step, a.dry_run) and ok
            if not ok:
                break
        results[key] = ok

    if a.dry_run:
        print("\nDry run: nothing was changed."); return
    st2, _ = detect_all(target)
    cfg = write_config(target, tools_dir, st2)
    filled = fill_brand(os.path.join(target, "brand.md"), cfg)
    print("\nResult:")
    for k, ok in results.items():
        print("  %-15s %s" % (k, "installed" if st2[k]["ok"] else ("failed: see messages above" if not ok else "not detected yet (open a new terminal and run the check again)")))
    if filled:
        print("  filled in brand.md: " + ", ".join(filled))
    print("  paths saved in " + os.path.join(tools_dir, "tools.json"))
    if all(st2[k]["ok"] for k in ("voice-packages", "kokoro-models", "whisper-model")) and any(k in results for k in ("voice-packages", "kokoro-models", "whisper-model")):
        selftest(tools_dir)


if __name__ == "__main__":
    main()
