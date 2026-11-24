---
name: shorts-publish
description: How a Short's publish pack is written (title, description, tags, hashtags, thumbnail, notes). Load before writing any upload metadata. Preparing the pack never means uploading.
---

# Publish pack

Files in `projects/<name>/publish/`: `title.txt`, `description.txt`, `tags.txt`, `hashtags.txt`, `NOTES.md`, the `.srt`, and the thumbnail in `thumbnails/<name>.png`.

## Title
Curiosity, plain words, one promise, about 70 characters or fewer, the topic in the first 40. Run `tools/titlecheck.py`. No clickbait the video cannot back up, no private information, no shouting.

## Description (in this order)
1. One sentence that repeats the promise.
2. "What this Short covers": 4-6 bullets, each a real thing in the video.
3. Dated facts with "checked <date>, recheck before relying on them".
4. A note when numbers on screen are examples.
5. Any disclaimer `brand.md` requires (for example educational only, not advice).
6. Voice and character disclosure, edited to match the video.
7. Sources with links, primary sources first, then a "Sound and image credits" block from `attribution.json` if Openverse was used.
8. The sign-off from `brand.md`, if any.
No private information, no affiliate or broker links.

## Tags and hashtags
About 20-25 tags: the topic, the questions people search (`shorts-seo`), the channel tag. At most three hashtags in the description.

## Thumbnail
Big number or one short phrase, high contrast, four words or fewer, different from the title, readable at phone size, no private information. Render it with whatever tool `brand.md` names (an HTML template and a headless browser work well) and look at the PNG.

## NOTES.md must say
- NOT uploaded; upload only after the user approves.
- Which dates and figures to recheck right before posting.
- What was left out on purpose and why.
- Which audio versions exist.
- The main keyword phrase and the pinned-comment draft marked "needs approval".

## Never
Upload, schedule, post a comment or reply.
