---
name: shorts-voice
description: Script voice, hook rules, content rules, disclosures and privacy for Shorts. Load before writing or editing any narration, on-screen text, title or description. Channel-specific wording comes from brand.md.
---

# Script voice and content rules

Read `brand.md` for tone, closing line, disclosures and topic rules. Defaults below apply when it is silent.

## Hook (first 2-3 seconds)
1. Confirm the title's promise in the first sentence.
2. Open a question the viewer cannot close yet.
3. Show the payoff exists (a number, a place, a thing moving).
- No channel intro, no "welcome back", no "before we start", no subscribe pitch before the payoff.
- Write five options in different shapes (`shorts-hooks`), score them, keep two, choose one.
- Never invent a number, result or source. If a figure would help and is not verified, write the line without it.

## Writing
- Short sentences, spoken language, one idea per sentence. Read each line aloud in your head.
- Run the `humanizer` skill if it is installed; otherwise remove AI tells yourself: "not X but Y" staging, one-line closers, forced triplets, stock hype words.
- Spell numbers as words in narration when `brand.md` says so (text-to-speech often garbles digits).
- Name the currency, unit and date for every figure. Future dates are re-checked on the primary source on the day of posting.

## Closing
Use the closing line from `brand.md`, if any.

## Disclosures
Add every disclosure `brand.md` lists. Common ones: AI-generated voice, fictional characters, example numbers labelled as examples, "educational, not advice" for money, health or legal topics.

## Privacy (hard rule)
No term from `shorts-kit.json` ("forbidden"), and never an email, IP address, home folder, address, workplace or device name, in any frame, subtitle, script or metadata. Search the files before finishing.
