r"""scaffold.py - set up a studio folder for Shorts Studio Kit.

Used by the /shorts:setup skill after a plugin install; also works on its own.

    python scaffold.py                    # set up the current folder
    python scaffold.py --target DIR       # set up another folder
    python scaffold.py --update-tools     # also replace tools/*.py with this kit's versions

Creates, only if missing: brand.md, shorts-kit.json, notes/queue.md, analytics/results.csv.
Copies the five helper scripts into tools/. A script you edited is kept unless --update-tools.
Adds a short section to CLAUDE.md once, and keeps shorts-kit.json (your private terms) in .gitignore.
Never deletes anything.
"""
import argparse, filecmp, os, shutil, sys

KIT = os.path.dirname(os.path.abspath(__file__))
MARK = "shorts-studio-kit:begin"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=os.getcwd())
    ap.add_argument("--update-tools", action="store_true")
    a = ap.parse_args()
    target = os.path.abspath(a.target)

    need = [os.path.join("templates", n) for n in ("brand.md", "shorts-kit.json", "queue.md", "results.csv", "CLAUDE-section.md")]
    bad = [n for n in need if not os.path.isfile(os.path.join(KIT, n))]
    if bad or not os.path.isdir(os.path.join(KIT, "tools")):
        sys.exit("kit is incomplete, missing: " + ", ".join(bad or ["tools/"]) + "\nNothing was changed.")

    os.makedirs(target, exist_ok=True)
    written, kept_tools, kept_files = [], [], []

    tools_dir = os.path.join(target, "tools")
    os.makedirs(tools_dir, exist_ok=True)
    for name in sorted(os.listdir(os.path.join(KIT, "tools"))):
        if not name.endswith(".py"):
            continue
        src, dst = os.path.join(KIT, "tools", name), os.path.join(tools_dir, name)
        if os.path.exists(dst):
            if filecmp.cmp(src, dst, shallow=False):
                continue
            if not a.update_tools:
                kept_tools.append(os.path.join("tools", name))
                continue
        shutil.copyfile(src, dst)
        written.append(os.path.join("tools", name))

    once = [("brand.md", "brand.md"), ("shorts-kit.json", "shorts-kit.json"),
            (os.path.join("notes", "queue.md"), "queue.md"), (os.path.join("analytics", "results.csv"), "results.csv")]
    for rel, tpl in once:
        dst = os.path.join(target, rel)
        if os.path.exists(dst):
            kept_files.append(rel)
            continue
        os.makedirs(os.path.dirname(dst) or target, exist_ok=True)
        shutil.copyfile(os.path.join(KIT, "templates", tpl), dst)
        written.append(rel)

    claude_md = os.path.join(target, "CLAUDE.md")
    if not os.path.exists(claude_md):
        open(claude_md, "w", encoding="utf-8", newline="\n").write("# Studio\n")
    if MARK not in open(claude_md, encoding="utf-8").read():
        section = open(os.path.join(KIT, "templates", "CLAUDE-section.md"), encoding="utf-8").read()
        open(claude_md, "a", encoding="utf-8", newline="\n").write(section)
        written.append("CLAUDE.md (section added)")

    gi = os.path.join(target, ".gitignore")
    have = open(gi, encoding="utf-8").read().splitlines() if os.path.exists(gi) else []
    add = [l for l in ("shorts-kit.json", ".env*", ".shorts-tools/") if l not in have]
    if add:
        with open(gi, "a", encoding="utf-8", newline="\n") as f:
            f.write(("\n" if have and have[-1] != "" else "") + "\n".join(add) + "\n")
        written.append(".gitignore (" + ", ".join(add) + ")")

    print("Shorts Studio Kit set up in " + target)
    print("  written: " + (", ".join(written) if written else "nothing new"))
    if kept_tools:
        print("  kept your edited scripts (use --update-tools to replace): " + ", ".join(kept_tools))
    if kept_files:
        print("  already present, not touched: " + ", ".join(kept_files))
    print("Next: fill in brand.md and shorts-kit.json, then type /shorts:short <your topic> (or /short if you installed with install.sh/ps1).")


if __name__ == "__main__":
    main()
