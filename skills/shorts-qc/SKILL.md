---
name: shorts-qc
description: Pre-release checklist for a finished Short (technical, factual, privacy, disclosure, credits). Load when checking a video before reporting it to the user.
---

# QC checklist

## Technical
- 1080x1920, 30 fps, H.264 with AAC 48 kHz stereo, within the length limit in `brand.md` (default 3:00), loudness about -14 LUFS.
- No frozen frames, no unintended black gaps, audio and picture the same length.
- Subtitles inside the safe area (text between about y 220 and 1600 of 1920), two rows at most, matching the narration.
- Stills at the start, middle, end and every scene change, and you looked at them.

## Content
- Every number and date on screen and in narration is in `research/<name>.md` with a source. Example numbers are labelled.
- Currency and units are named. Future dates are rechecked or flagged in `NOTES.md`.
- The narration, transcribed, matches `storyboard/script.md` word for word (digits in the transcript for spoken numbers are fine). So do the burned subtitles and the on-screen captions. A script that differs from the shipped video is a FAIL for the script stage.
- Every factual claim in the shipped narration and captions, including small ones ("no magnet", "metal teeth"), is backed by the research note, not only the claims in the script.
- No AI tells in the script.

## Privacy
Search the script, subtitles, scene scripts, description, tags and notes for every term in `shorts-kit.json` ("forbidden"), plus email addresses, IP addresses, home folders (`C:\Users`, `/home/`) and device names. Zero hits allowed.

## Disclosures and rules
- Every disclosure in `brand.md` is present.
- No logos, no profit or result promises, no affiliate links.
- Every file taken from Openverse has an entry in `attribution.json` and a credit line in the description. Licences are cc0, pdm or by only.
- Nothing was uploaded, no account or key was created, no finished export was overwritten.

## Result format
`PASS` or `FAIL`, then findings, each with the file or timestamp, what is wrong, and which stage should fix it.
