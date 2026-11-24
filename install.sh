#!/usr/bin/env bash
# Shorts Studio Kit installer (macOS, Linux, Git Bash).
#
#   ./install.sh                  install into the current folder
#   ./install.sh /path/to/studio  install into another folder
#   ./install.sh --force [dir]    overwrite kit files that differ (brand.md and your data are never overwritten)
#
# Installs skills and agents into <target>/.claude/, scripts into <target>/tools/, and creates
# brand.md, shorts-kit.json, notes/queue.md and analytics/results.csv if they do not exist yet.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE=0; TARGET=""
for a in "$@"; do
  case "$a" in --force) FORCE=1 ;; *) TARGET="$a" ;; esac
done
TARGET="${TARGET:-$PWD}"
mkdir -p "$TARGET"; TARGET="$(cd "$TARGET" && pwd)"
copied=0; skipped=(); kept=0

# preflight: refuse to start if the kit itself is incomplete, so a bad download never leaves a half install
missing=0
for f in templates/brand.md templates/shorts-kit.json templates/queue.md templates/results.csv templates/CLAUDE-section.md; do
  [ -f "$KIT/$f" ] || { echo "kit is incomplete, missing: $f" >&2; missing=1; }
done
for d in skills agents tools; do
  [ -n "$(ls -A "$KIT/$d" 2>/dev/null)" ] || { echo "kit is incomplete, empty or missing: $d/" >&2; missing=1; }
done
[ "$missing" -eq 0 ] || { echo "Nothing was installed. Re-download the kit and try again." >&2; exit 1; }

copy_kit() {   # kit-owned file: copy if missing or identical, skip if you edited it (unless --force)
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ]; then
    cmp -s "$src" "$dst" && return 0
    if [ "$FORCE" -eq 0 ]; then skipped+=("$dst"); return 0; fi
  fi
  cp "$src" "$dst"; copied=$((copied + 1))
}
copy_once() {  # user-owned file: create only if missing
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ]; then kept=$((kept + 1)); return 0; fi
  cp "$src" "$dst"; copied=$((copied + 1))
}

for d in "$KIT"/skills/*/; do
  n="$(basename "$d")"; copy_kit "$d/SKILL.md" "$TARGET/.claude/skills/$n/SKILL.md"
done
for f in "$KIT"/agents/*.md; do copy_kit "$f" "$TARGET/.claude/agents/$(basename "$f")"; done
for f in "$KIT"/tools/*.py;  do copy_kit "$f" "$TARGET/tools/$(basename "$f")"; done

copy_once "$KIT/templates/brand.md"        "$TARGET/brand.md"
copy_once "$KIT/templates/shorts-kit.json" "$TARGET/shorts-kit.json"
copy_once "$KIT/templates/queue.md"        "$TARGET/notes/queue.md"
copy_once "$KIT/templates/results.csv"     "$TARGET/analytics/results.csv"

CLAUDE="$TARGET/CLAUDE.md"
[ -e "$CLAUDE" ] || printf '# Studio\n' > "$CLAUDE"
if ! grep -q 'shorts-studio-kit:begin' "$CLAUDE"; then cat "$KIT/templates/CLAUDE-section.md" >> "$CLAUDE"; copied=$((copied + 1)); fi

# keep private terms out of git
GI="$TARGET/.gitignore"; touch "$GI"
for line in 'shorts-kit.json' '.env*' '.shorts-tools/'; do grep -qxF "$line" "$GI" || echo "$line" >> "$GI"; done

echo
echo "Shorts Studio Kit installed into $TARGET"
echo "  files written: $copied"
if [ "${#skipped[@]}" -gt 0 ]; then echo "  kept your edited versions (use --force to overwrite):"; printf '    %s\n' "${skipped[@]}"; fi
[ "$kept" -gt 0 ] && echo "  already present, not touched: $kept template file(s)"
# pick a Python that really runs (on Windows, python3 can be a Microsoft Store stub that only prints a message)
PY=""
for c in python3 python py; do
  if "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "  WARNING: Python 3 was not found. Install Python 3.10 or newer, then run: python tools/setup_tools.py --install"
else
  # Shows what is installed and what is missing (ffmpeg, local voice, Whisper). Installs only after your yes.
  if ( : < /dev/tty ) 2>/dev/null; then "$PY" "$TARGET/tools/setup_tools.py" --target "$TARGET" --installer-mode < /dev/tty || true
  else "$PY" "$TARGET/tools/setup_tools.py" --target "$TARGET" --installer-mode < /dev/null || true; fi
fi
echo
echo "Next:"
echo "  1. Fill in brand.md and shorts-kit.json (your private terms; this file stays out of git)."
echo "  2. Open Claude Code in $TARGET and type:  /short <your topic>"
