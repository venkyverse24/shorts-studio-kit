---
name: shorts-setup
description: One-time setup of a studio folder for Shorts Studio Kit after a plugin install. Creates brand.md, shorts-kit.json, the helper scripts in tools/, a queue file and a results log, then walks the user through filling in brand.md. Use when the user types /shorts:setup, says "set up the shorts kit", or when brand.md or tools/hookscore.py is missing in the current folder.
---

# Set up this folder

1. Work in the folder the user opened Claude Code in (the studio folder). Do not create the studio anywhere else.
2. Run the scaffold script. After a plugin install the path below is filled in by Claude Code:
   `python "${CLAUDE_PLUGIN_ROOT}/scaffold.py" --target .`
   Use `python3` or `py` if `python` is not found. If the path above still shows a literal `${CLAUDE_PLUGIN_ROOT}`, the kit was installed with `install.sh` or `install.ps1`, which already did this step: skip to step 4.
3. Read the script's summary back to the user in two lines: what was created, what was kept. It never overwrites `brand.md`, `shorts-kit.json` or edited scripts.
4. Help fill in `brand.md`. Ask only for what is missing, in this order, and write the answers into the file:
   - channel name, niche, narration language, typical length, uploads per week
   - tone, words never to use, closing line (may be empty), number style
   - disclosures that must appear (for example AI-generated voice)
   - which tools exist on this machine: the renderer (for example Blender, or "simple Python frames and ffmpeg"), the narration tool or "I record my own voice", ffmpeg, and the Python command
   Never invent tool paths: check that each path the user gives exists.
5. Ask for private terms to block (their name, usernames, hostnames, employer, suburb, anything that must never appear in a video) and write them into `shorts-kit.json` under `forbidden`. Remind them that this file stays out of git.
6. Finish with the next step: `/shorts:short <topic>` (or `/short <topic>` for the install-script route). Say plainly that nothing is ever uploaded, and that the first full run uses their own Claude plan or API usage.

Never upload, post, create accounts or keys, or install paid tools while setting up.
