---
name: shorts-comments
description: Triage comments on a channel's videos and draft replies and pinned comments in the channel voice. Drafts only; the user posts. Use when the user pastes comments or asks for a pinned comment.
---

# Comments (drafts only)

Claude never posts, replies, hearts or deletes. Drafts go in `projects/<name>/publish/comments_drafts.md` and the user approves and posts.

## Triage (when the user pastes comments)
Group: question, correction, praise, topic request, criticism, spam or abuse, private-information bait (asks where the creator lives or works, or for private details).
- Corrections: check against `research/<name>.md` first. If the viewer is right, draft a thank-you, state the fix, and add it to the open items.
- Topic requests: add to the idea list in `notes/queue.md`.
- Spam, abuse, bait: no reply, flag for the user.

## Draft style
- Under 30 words, plain and friendly, answers the actual question, no sales language, no AI tells.
- Money, health or legal topics: no advice, no targets, no "buy" opinions; say it is educational.
- Never reveal private information, location, workplace, device names or servers. Never promise a video date.
- No links except official sources already in the description.

## Pinned comment
One short comment: what was made and how (in general terms), a pointer to the sources in the description, any disclaimer from `brand.md`, and one question to start a discussion. Mark it "needs approval" and wait.
