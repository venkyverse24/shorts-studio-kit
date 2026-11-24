---
name: shorts-3d
description: Craft rules for cinematic 3D Shorts in Blender (what makes a shot feel alive, a safe build process, common crashes). Load before any Blender work. Tool paths come from brand.md.
---

# 3D Shorts in Blender

## Why a Short reads as a slideshow
Every shot needs:
1. A real place with architecture, not props on a pedestal.
2. A character doing a task, not standing.
3. A moving machine or vehicle.
4. A camera move that has a reason.
5. The story object travelling through the shot.
No shot longer than about three seconds without a cut or a new motion beat.

## Process
- Format: 1080x1920, 30 fps. Previews at 540x960 and 15 fps.
- One project folder per film: `PLAN.md`, `storyboard/`, `audio/`, `scripts/`, `previews/`, `finals/`, `publish/`, `backups/`.
- Build timing from the real narration (`audio/timing.json`), not guesses.
- Build one scene at a time. Render a preview, extract stills, look at them, fix, then continue. Watch the final video before reporting.
- Copy helper scripts into the project instead of editing shared ones.
- Back up before changing a working scene. Never overwrite a finished export.

## Blender gotchas
- Never run two Blender renders at once (memory and graphics-context crashes). Stop stray render processes before starting another.
- "No OpenGL vendor" at startup means the graphics driver is in a bad state: reset it (Windows: Win+Ctrl+Shift+B) or restart, and do not loop on retries.
- Key arm and head poses on `rotation_quaternion` when the rig uses quaternions. Mixing in euler keys gives snapping.
- Delete leftover per-frame keys from a base animation when you overlay a new pose.
- Hold objects by parenting or constraining them to hand bones, not by keyframing positions.
- Seated poses: rotate upper legs forward and lower legs back at the hips and knees; check from the side.
- Short rigs crouch if walk cycles tuned for taller legs are reused: refit stride and hip height to the leg length.
- Out-of-memory during render: close other programs, lower the sample count for previews, and render in passes.

## Always
Stills at the start, middle, end and every scene change before reporting.
