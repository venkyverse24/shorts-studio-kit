---
name: shorts-plan
description: Refresh the Shorts queue from what performed. Use when the user asks what to make next, for a weekly plan, or after a channel audit.
---

# Queue refresh

Queue file: `notes/queue.md`.

1. Read `brand.md`, the queue, `python tools/analytics.py report` and the latest `analytics/audit_*.md`.
2. Keep the direction the numbers support. With few videos, say so and keep a mix of formats so there is something to compare.
3. Reorder, drop or add topics:
   - Move up topics that match a top performer's format and topic family.
   - Do not run the same topic family back to back.
   - Add 3-5 ideas from `python tools/ytsuggest.py "<seed>" --expand` and from web research, each phrased as a question a viewer would type.
   - Mark topics that need verified dates or data so research starts early.
4. Do not delete history: append a dated section "Refreshed <date>" with the new order and one line of reasoning per change.
5. Weekly view: one slot per upload day from `brand.md`, with a note on which builds take longer (3D films take far longer than simple animation) and the limit of one Blender render at a time.
6. Show the new top five and ask for approval before building the first one.
