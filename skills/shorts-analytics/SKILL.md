---
name: shorts-analytics
description: Learn from published Shorts - log views and retention, find where viewers leave, rank what worked, audit the channel. Use after a Short is live, when the user brings numbers, or for a monthly channel review.
---

# After publishing

Claude cannot log in to YouTube Studio. The user supplies numbers by reading them out, pasting them, or exporting a CSV. Never open Studio on your own.

## Log a video
`python tools/analytics.py add --name <Name> --title "..." --published YYYY-MM-DD --length <s> --views <n> --avp <avg view %> --format <style> --topic <topic> --hook "<first line>" --source "Studio read <date>"`
The log is `analytics/results.csv`. To fix a number, edit the CSV and keep a note.

## Rank
`python tools/analytics.py report` shows views against the channel median and the median by format and topic. With fewer than about ten videos, patterns are hints only: say so.

## Where viewers leave
Studio -> video -> Analytics -> Engagement -> Audience retention, then export the chart data if possible, or read out values at a few seconds.
`python tools/analytics.py retention <csv> --length <s> --timing projects/<name>/audio/timing.json`
It prints retention at 1, 3, 10 and 30 seconds, the end value, and the three biggest drops, mapped to scenes when timing exists. The parser looks for a time or percent-of-video column and a retention column and says plainly when it cannot find them; if it fails, ask for the header line and adapt it. Open the script at those seconds, say what happens there, and propose one change. Do not claim the cause is proven.

## Monthly audit
1. Update the log for every video.
2. `report`, then name the top and bottom two and what differs: format, topic, hook shape (`shorts-hooks`), length, thumbnail, post time.
3. Write `analytics/audit_<YYYY-MM>.md`: what to repeat, what to stop, what to test next. Test one change at a time.
4. Update `shorts-hooks` and the queue (`shorts-plan`) only with what at least two videos support.

## Rules
No private information in any file. Never post, reply or change anything on YouTube.
