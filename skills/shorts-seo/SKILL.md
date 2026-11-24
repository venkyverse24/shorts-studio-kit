---
name: shorts-seo
description: Keyword step for a Short: what people type into YouTube search, then title, description opening and tags built from it. Load before writing a title, description or tags.
---

# Keyword step

1. `python tools/ytsuggest.py "<topic phrase>"`, and add `--expand` for more. It uses YouTube's public autocomplete, so it shows what people search for. It is an unofficial endpoint: if it stops answering, use WebSearch for "people also ask" style questions.
2. Pick one main phrase that reads as a natural question or promise, plus 5-8 related phrases for tags.
3. Put the main phrase in the first 40 characters of the title when it reads naturally, and in the first sentence of the description. Never stuff keywords.
4. Tags: the main phrase, the related phrases, topic words, the channel name from `brand.md`. About 20-25 tags, nothing misleading, no other creators' names.
5. `python tools/titlecheck.py --title "..." --thumb "..."` and fix every FAIL.
6. Record the main phrase and the suggestions in `projects/<name>/publish/NOTES.md` so `shorts-analytics` can later compare phrase against performance.

Suggestions show demand, not competition. Prefer a phrase the video can answer more clearly or more visually than a text explainer can.
