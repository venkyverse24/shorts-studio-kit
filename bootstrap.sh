#!/usr/bin/env bash
# Shorts Studio Kit: one-command install (macOS, Linux, Git Bash). No git needed.
#
#   curl -fsSL https://raw.githubusercontent.com/venkyverse24/shorts-studio-kit/main/bootstrap.sh | bash
#
# Downloads the kit, installs it into the current folder (or $KIT_TARGET), and removes the download.
# Prefer to read it first? Download this file, read it, then run it: it only downloads the kit zip
# and runs the kit's own install.sh.
#
# Settings (environment variables):
#   KIT_REPO    owner/repo on GitHub, e.g. for a fork   (default: venkyverse24/shorts-studio-kit)
#   KIT_REF     branch or tag to install, e.g. v1.1.0   (default: main)
#   KIT_TARGET  studio folder                           (default: current folder)
#   KIT_ZIP     a local zip path or URL instead of GitHub (for testing and offline use)
set -euo pipefail

REPO="${KIT_REPO:-venkyverse24/shorts-studio-kit}"
REF="${KIT_REF:-main}"
TARGET="${KIT_TARGET:-$PWD}"
SRC="${KIT_ZIP:-https://github.com/$REPO/archive/$REF.zip}"

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
echo "Downloading the kit..."
case "$SRC" in
  http://*|https://*) curl -fsSL "$SRC" -o "$tmp/kit.zip" ;;
  *) cp "$SRC" "$tmp/kit.zip" ;;
esac

mkdir -p "$tmp/x"
if command -v unzip >/dev/null 2>&1; then unzip -q "$tmp/kit.zip" -d "$tmp/x"
else
  PYZ=""
  for c in python3 python py; do
    if "$c" -c "import zipfile" >/dev/null 2>&1; then PYZ="$c"; break; fi
  done
  [ -n "$PYZ" ] || { echo "Need unzip or Python to unpack the kit." >&2; exit 1; }
  "$PYZ" -m zipfile -e "$tmp/kit.zip" "$tmp/x"
fi

kit="$(find "$tmp/x" -maxdepth 2 -name install.sh -print -quit | xargs -I{} dirname {})"
[ -n "$kit" ] && [ -f "$kit/install.sh" ] || { echo "install.sh not found in the download. Nothing was installed." >&2; exit 1; }

bash "$kit/install.sh" "$TARGET"
