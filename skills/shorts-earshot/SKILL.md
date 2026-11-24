---
name: shorts-earshot
description: Make sound effects for Shorts with Earshot, an open-source tool that renders effects from code (no recordings, no licence work). Includes how to review it before installing. Use when a Short needs whooshes, hits, clicks, doors or ambience.
---

# Earshot (optional third-party tool)

Earshot is a separate open-source project by Leon Lin (MIT): https://github.com/Leonxlnx/earshot. It is not part of this kit and is not installed by it. The PyPI package named "earshot" is a different project, so install from the GitHub URL.

## Install only after you review it
1. Clone it into a folder of your choice and read the code. When this skill was written, a review of the package found only ffmpeg and ffprobe subprocess calls with fixed arguments, NumPy loads with pickle disabled, and no sockets or telemetry. An optional `llm` command uploads audio to a cloud model and needs an API key: never use it.
2. Pin the commit you reviewed. Install into its own virtual environment, not into your studio's environment:
   `python -m venv <folder>/earshot-venv` then `<folder>/earshot-venv/bin/pip install <path to the clone>` (on Windows use `Scripts\pip`).
3. If your CPU is old and import fails with an `X86_V2` error, install `numpy==1.26.4`, `scipy<1.14`, `numba<0.61` in that environment.
4. Do not install the "listen" extras (torch and about a gigabyte of models) unless you want them. Without them the describe, critique and match commands do not work and a person has to listen.
5. Do not register it as a Claude Code plugin or MCP server unless you accept third-party code starting with every session. Do not run `npx skills add` from it.
6. Write the install folder into `brand.md` ("Sound effects: Earshot install folder").

## Use
```
earshot sounds --search whoosh
earshot make "a deep whoosh transition" -o sfx/whoosh.wav
earshot sfx render whoosh_fast/crisp -o sfx/w.wav --dur 0.8 --apex 0.32
earshot sfx check sfx/w.wav
```
Whole film: `earshot kit init --preset launch -o kit.json`, edit cue times to the real narration timing, `earshot kit render kit.json --out kit`, `earshot kit check`, `earshot kit audition`.
Output is 48 kHz stereo WAV.

## Check every sound
- The tool prints what it understood. "not understood: <word>" means it guessed (a free-text request for a specific object can return a generic sound). Search `earshot sounds --search <word>` and use a named bank id instead.
- Run `earshot sfx check` (clicks, clipping, truncation) and listen before mixing.
- Never use `earshot llm` or upload audio anywhere.
