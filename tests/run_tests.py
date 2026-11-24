"""Smoke tests for Shorts Studio Kit. Standard library only.   python tests/run_tests.py"""
import csv, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)


def run(args, cwd=None):
    p = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr


def frontmatter(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", t, re.S)
    return dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l) if m else {}


# structure
skills = sorted(d for d in os.listdir(os.path.join(ROOT, "skills")))
agents = sorted(f for f in os.listdir(os.path.join(ROOT, "agents")) if f.endswith(".md"))
check(len(skills) == 14, f"14 skills present ({len(skills)})")
check(len(agents) == 7, f"7 agents present ({len(agents)})")
for s in skills:
    fm = frontmatter(os.path.join(ROOT, "skills", s, "SKILL.md"))
    check(fm.get("name", "").strip() == s and len(fm.get("description", "")) > 40, f"skill {s}: name matches folder, has description")
for a in agents:
    fm = frontmatter(os.path.join(ROOT, "agents", a))
    check(fm.get("name", "").strip() == a[:-3] and "tools" in fm, f"agent {a[:-3]}: name matches file, tools listed")

# every skill or tool named in the CLAUDE section exists
section = open(os.path.join(ROOT, "templates", "CLAUDE-section.md"), encoding="utf-8").read()
for n in set(re.findall(r"`(shorts-[a-z0-9-]+)`", section)):
    check(n in skills, f"CLAUDE section mentions existing skill {n}")
for n in set(re.findall(r"`(tools/[a-z]+\.py)`", section)):
    check(os.path.exists(os.path.join(ROOT, n)), f"CLAUDE section mentions existing script {n}")

# the installer's inputs must be committed (a git-ignored template breaks a fresh clone)
need = ["templates/brand.md", "templates/shorts-kit.json", "templates/queue.md", "templates/results.csv", "templates/CLAUDE-section.md", "install.sh", "install.ps1", "bootstrap.sh", "bootstrap.ps1", "scaffold.py", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "skills/shorts-setup/SKILL.md"]
if os.path.isdir(os.path.join(ROOT, ".git")):
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    untracked_ok = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for n in need:
        check(n in tracked or n in untracked_ok, f"installer input {n} is tracked or addable (not git-ignored)")

# PowerShell installer must parse (the shell test cannot catch a broken .ps1)
import shutil
ps = shutil.which("pwsh") or shutil.which("powershell")
if ps:
    for script in ("install.ps1", "bootstrap.ps1"):
        cmd = "$e=$null;$t=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('%s',[ref]$t,[ref]$e);if($e){$e|%%{$_.Message};exit 1}" % (ROOT + "/" + script)
        p = subprocess.run([ps, "-NoProfile", "-Command", cmd], capture_output=True, text=True)
        check(p.returncode == 0, script + " parses with PowerShell: " + (p.stdout.strip()[:120] or "ok"))
else:
    print("SKIP PowerShell parse checks (PowerShell not found)")
bash = shutil.which("bash")
if bash:
    for script in ("install.sh", "bootstrap.sh"):
        p = subprocess.run([bash, "-n", os.path.join(ROOT, script)], capture_output=True, text=True)
        check(p.returncode == 0, script + " passes bash -n: " + (p.stderr.strip()[:120] or "ok"))

# plugin manifests (what Claude Code reads when the kit is installed as a plugin)
mk = json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
pj = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8"))
entry = mk["plugins"][0]
check(entry["name"] == pj["name"], "marketplace plugin name matches plugin.json name")
check(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pj["name"]) is not None and not pj["name"].startswith(("claude-", "anthropic-", "anthropics-")), "plugin name is kebab-case and not a reserved prefix")
check(entry["source"] == "./" and "owner" in mk and mk.get("name"), "marketplace has name, owner and a root-plugin source")

# scaffold script (used by /shorts:setup)
with tempfile.TemporaryDirectory() as d:
    target = os.path.join(d, "studio")
    code, out = run([os.path.join(ROOT, "scaffold.py"), "--target", target])
    made = all(os.path.exists(os.path.join(target, f)) for f in ("brand.md", "shorts-kit.json", "CLAUDE.md", ".gitignore", "tools/hookscore.py", "notes/queue.md", "analytics/results.csv"))
    check(code == 0 and made, "scaffold.py sets up an empty folder")
    open(os.path.join(target, "brand.md"), "w", encoding="utf-8").write("mine")
    code, out = run([os.path.join(ROOT, "scaffold.py"), "--target", target])
    kept = open(os.path.join(target, "brand.md"), encoding="utf-8").read() == "mine"
    once = open(os.path.join(target, "CLAUDE.md"), encoding="utf-8").read().count("shorts-studio-kit:begin") == 1
    check(code == 0 and kept and once, "scaffold.py rerun keeps brand.md and adds the CLAUDE.md section once")
    check("shorts-kit.json" in open(os.path.join(target, ".gitignore"), encoding="utf-8").read(), "scaffold.py keeps shorts-kit.json out of git")

# tools run
for t in ("hookscore", "titlecheck", "ytsuggest", "openverse", "analytics", "setup_tools"):
    code, out = run(["-W", "error", "-c", f"import ast;ast.parse(open(r'{ROOT}/tools/{t}.py',encoding='utf-8').read())"])
    check(code == 0, f"tools/{t}.py parses cleanly")

code, out = run([os.path.join(ROOT, "tools", "hookscore.py"), "--examples"])
check(code == 0 and "greeting (bad)" in out and "WEAK" in out, "hookscore --examples runs and flags the bad hook")

with tempfile.TemporaryDirectory() as d:
    json.dump({"forbidden": ["zebraname"], "banned_phrases": ["Episode"], "allowed_caps": ["LIDAR"]}, open(os.path.join(d, "shorts-kit.json"), "w"))
    code, out = run([os.path.join(ROOT, "tools", "titlecheck.py"), "--title", "How zebraname made a thing?"], cwd=d)
    check(code == 1 and "private information" in out, "titlecheck blocks a forbidden term from shorts-kit.json")
    code, out = run([os.path.join(ROOT, "tools", "titlecheck.py"), "--title", "Contact me@example.com about this"], cwd=d)
    check(code == 1, "titlecheck blocks an email address without any config")
    code, out = run([os.path.join(ROOT, "tools", "titlecheck.py"), "--title", "How does LIDAR see in the dark?", "--thumb", "TINY CHIPS"], cwd=d)
    check(code == 0, "titlecheck passes a clean title")
    code, out = run([os.path.join(ROOT, "tools", "hookscore.py"), "--hook", "How did zebraname know where you are?"], cwd=d)
    check("clean 0" in out, "hookscore zeroes CLEAN for a forbidden term")

    # analytics: add, report, retention on made-up data
    a = os.path.join(ROOT, "tools", "analytics.py")
    os.makedirs(os.path.join(d, "analytics"))
    shutil_tools = os.path.join(d, "tools"); os.makedirs(shutil_tools)
    open(os.path.join(shutil_tools, "analytics.py"), "w", encoding="utf-8").write(open(a, encoding="utf-8").read())
    at = os.path.join(shutil_tools, "analytics.py")
    for name, v in (("A", 100), ("B", 40), ("C", 60)):
        code, _ = run([at, "add", "--name", name, "--views", str(v), "--format", "3d", "--topic", "x"], cwd=d)
    code, out = run([at, "report"], cwd=d)
    check(code == 0 and "3 videos" in out and "median 60" in out, "analytics add + report")
    rows = [["Video position (%)", "Audience retention (%)"]] + [[i / 100, (100 - 0.4 * i - (20 if i >= 50 else 0)) / 100] for i in range(101)]
    csv.writer(open(os.path.join(d, "ret.csv"), "w", newline="")).writerows(rows)
    code, out = run([at, "retention", os.path.join(d, "ret.csv"), "--length", "60"], cwd=d)
    check(code == 0 and "biggest drops" in out and "30 s" in out, "analytics retention finds drops")

# setup_tools: planning per OS, status, brand.md fill, pinned model files
import importlib.util
spec = importlib.util.spec_from_file_location("setup_tools", os.path.join(ROOT, "tools", "setup_tools.py"))
st_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(st_mod)
check(all(len(h) == 64 and sz > 1000000 for sz, h in st_mod.MODELS.values()), "setup_tools pins size and SHA-256 for both Kokoro files")
check("av<19" in st_mod.PY_PACKAGES, "setup_tools pins av<19 (av 19 breaks faster-whisper transcribe)")
with tempfile.TemporaryDirectory() as d:
    def dry(os_name, *extra):
        env = dict(os.environ, SHORTS_TOOLS_FAKE_OS=os_name, SHORTS_TOOLS_ASSUME_MISSING="ffmpeg,blender,voice-packages,kokoro-models,whisper-model")
        p = subprocess.run([PY, os.path.join(ROOT, "tools", "setup_tools.py"), "--target", d, "--install", "--dry-run", "--with", "blender"] + list(extra), capture_output=True, text=True, env=env)
        return p.returncode, p.stdout
    code, out = dry("windows"); check(code == 0 and "winget install --id Gyan.FFmpeg" in out and "BlenderFoundation.Blender" in out and "Dry run: nothing was changed" in out, "setup_tools plans winget installs on Windows")
    code, out = dry("mac"); check("brew install ffmpeg" in out and "brew install --cask blender" in out, "setup_tools plans Homebrew installs on macOS")
    code, out = dry("linux"); check("sudo apt-get install -y ffmpeg" in out, "setup_tools plans apt installs on Linux (sudo is never run silently)")
    check(not os.path.exists(os.path.join(d, ".shorts-tools")), "setup_tools dry run creates nothing")
    p = subprocess.run([PY, os.path.join(ROOT, "tools", "setup_tools.py"), "--target", d, "--json"], capture_output=True, text=True)
    status = json.loads(p.stdout); check({"python", "ffmpeg", "voice-packages", "kokoro-models", "whisper-model", "blender"} <= set(status), "setup_tools --json reports every tool")
    p = subprocess.run([PY, os.path.join(ROOT, "tools", "setup_tools.py"), "--target", d, "--installer-mode"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    check(p.returncode == 0 and not os.path.exists(os.path.join(d, ".shorts-tools")), "setup_tools installer mode with no terminal only shows the table")
    brand = os.path.join(d, "brand.md"); shutil.copyfile(os.path.join(ROOT, "templates", "brand.md"), brand)
    cfg = {"python": "python", "venv_python": "V/python", "ffmpeg": "F/ffmpeg", "ffprobe": "F/ffprobe", "kokoro_model": "M/k.onnx", "kokoro_voices": "M/v.bin", "whisper_model": "small.en", "blender": None}
    filled = st_mod.fill_brand(brand, cfg); text = open(brand, encoding="utf-8").read()
    check(len(filled) == 4 and "Kokoro, local" in text and "F/ffmpeg" in text, "setup_tools fills the empty tool lines in brand.md")
    open(brand, "w", encoding="utf-8").write(text.replace("- Python command (python, python3, py): python", "- Python command (python, python3, py): mine"))
    st_mod.fill_brand(brand, dict(cfg, python="other"))
    check("Python command (python, python3, py): mine" in open(brand, encoding="utf-8").read(), "setup_tools never overwrites a tool line you filled in")

print("\n%d failed" % len(fails) if fails else "\nall passed")
sys.exit(1 if fails else 0)
