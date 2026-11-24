---
name: short
description: Make a YouTube Short from a one-line topic, end to end, using the kit's agents. Use for "/short <topic>", "make a short about X", "next short in the queue", or "revise <name>". Builds everything locally and never uploads.
---

# /short <topic>

You are the director. Read `brand.md` first. The user gives a topic or says "next in the queue" (`notes/queue.md`). Do not ask for details the skills already answer. Choose a folder name `<Topic_Name>`; a new version gets a new name and a finished one is never overwritten.

## Pipeline (each agent reads what the previous one wrote)
1. **short-researcher** -> `research/<name>.md` (facts with source links and dates, open items).
2. **short-scriptwriter** -> `projects/<name>/storyboard/script.md` (scene-by-scene narration, humanised, hook scored with `tools/hookscore.py`).
3. **short-sound, phase A** -> narration, voice mix, subtitles and `audio/timing.json` (`shorts-sound`, plus `shorts-earshot` and `shorts-openverse` if effects are wanted). Done first so the picture is timed to real speech.
4. **short-director** -> scenes, previews and a silent final render timed to `audio/timing.json` (`shorts-3d` for Blender, or the renderer named in `brand.md`). Look at stills before moving on.
5. **short-sound, phase B** -> combine audio and video, final checks.
6. **short-qc** -> PASS or FAIL report. On FAIL, send each finding back to the agent that owns it, then run QC again.
7. **short-publisher** -> title, description, tags, thumbnail, notes (`shorts-publish`, `shorts-seo`, `shorts-hooks`).

## How to run the agents
- Run every agent in the **foreground, one at a time**, and wait for its result before starting the next. Never use background mode and never end your turn while an agent is still working: in a non-interactive run the session exits and kills the render or encode in progress.
- Do not run the director and sound agents in parallel. On one machine they compete for memory (a transcript check crashed while a render was running). Order: researcher, scriptwriter, sound (narration first, so scene timing is real), director (cuts timed to that narration), sound again (mix with the finished video), qc, publisher.
- After sound phase A, compare the transcript with `storyboard/script.md`. They must match. If they do not, fix the script stage or the narration before the director starts, because the research check and QC rely on the script.
- After each agent returns, check that its output files exist and open (`ffprobe` for video and audio) before moving on.

## Stop point
Report: the video path, length, QC result, title, and anything that needs a decision. Then stop.

## After it is live
When the user brings view numbers, a retention export or comments, hand them to **channel-analyst** (`shorts-analytics`, `shorts-plan`, `shorts-comments`). Nothing is ever posted by Claude.

## Never without asking
Upload, schedule, publish, post comments, create accounts or keys, spend paid credits, or overwrite a finished export.

## Resume
If `projects/<name>/` exists, read its PLAN or notes and continue from the last finished stage. Do not redo research. A stage is finished only if its output opens: run `ffprobe` on every video and audio file first, and treat a file that fails to open (for example "moov atom not found") as an interrupted render to redo, not as done.
