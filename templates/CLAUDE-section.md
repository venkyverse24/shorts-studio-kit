
<!-- shorts-studio-kit:begin -->
## Shorts Studio Kit
Read `brand.md` first: it holds this channel's voice, rules, tools and folders. Private terms are in `shorts-kit.json`.

Short prompt: `/short <topic>` or "next short in the queue". It runs the agents in order and stops at a report:
`short-researcher` -> `short-scriptwriter` -> `short-director` -> `short-sound` -> `short-qc` -> `short-publisher`.
After a Short is live, `channel-analyst` handles numbers, retention, the queue and comment drafts.

Rules live in skills, not in prompts: `shorts-voice`, `shorts-hooks`, `shorts-seo`, `shorts-3d`, `shorts-sound`,
`shorts-earshot`, `shorts-openverse`, `shorts-setup`, `shorts-publish`, `shorts-qc`, `shorts-analytics`, `shorts-plan`, `shorts-comments`.
Helper scripts: `tools/hookscore.py`, `tools/titlecheck.py`, `tools/ytsuggest.py`, `tools/analytics.py`, `tools/openverse.py`, `tools/setup_tools.py`.

Never upload, post, reply, create accounts or use paid services without asking.
<!-- shorts-studio-kit:end -->
