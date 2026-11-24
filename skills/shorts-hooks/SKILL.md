---
name: shorts-hooks
description: Hook shapes for Shorts, plus how to score hook options and lint a title and thumbnail with the kit's scripts. Load when writing or choosing a hook, a title or thumbnail text.
---

# Hooks

Five shapes that work for explainer Shorts. Reuse the shape, never the words.

| Shape | Example | Notes |
|---|---|---|
| **Constraint, then puzzle** | "Your coat zip has no glue and no hooks. So how does it never come apart?" | The question carries a rule that makes it look impossible. |
| **Scene, then question** | "You stop at a red light and it turns green the moment you arrive. No camera, no switch, nobody watching. How did it know?" | A person doing something. Needs a visual that moves at once. |
| **Before and after** | "Phone cameras went from this to this in fifteen years." | The picture does the work; the text alone scores low. |
| **Everyone wants X, but...** | "Everyone wants a faster commute. But where does the time actually go?" | Trim to one question. |
| **Big claim** | "One invention changed how every city is built." | Weakest: no question. Use only with a strong picture. |

## Process
1. Write five hook options in different shapes into `projects/<name>/storyboard/hooks.txt`, one per line.
2. `python tools/hookscore.py projects/<name>/storyboard/hooks.txt` (use the Python command in `brand.md`). Six checks, 0-100 each: gap (open question), puzzle (a rule that looks impossible, then the question), viewer (you or a person), specific (a number or named thing, no hype), pace (about 4-8 seconds spoken), clean (no greeting, no digits, no private terms). The score is the average, capped at 49 if any one check is below 25. Bands: GOOD 70+, OK 50-69, WEAK below 50.
3. Keep the top two, show both with scores, choose one, and say what is on screen in the first two seconds.
4. Title and thumbnail: `python tools/titlecheck.py --title "..." --thumb "..."`. Fix every FAIL. Thumbnail text is four words or fewer and adds something the title does not say.

## Accuracy beats the score
Choose the hook by accuracy first and score second. Reject any option with a claim the research note does not back, even if it scores highest. Words like "only", "nothing", "no X", "never", "always", "alone" turn a supported fact into an exclusivity or absence claim: use only the research note's own wording for them. In a test, an earlier version of the scorer rewarded "only", and a hook saying "Only shape locks the teeth" outscored the exact sourced wording; the sourced wording is the one that passed QC. The scorer no longer rewards "only", but any score can be gamed, so the research note decides.

## What the scorer can and cannot do
It is a lint, not a prediction. It catches greetings, digits, missing questions, over-long hooks and private terms. `python tools/hookscore.py --examples` shows how it scores sample hooks. A picture-led hook can score low and still perform, so a low score is a reason to look again, not an automatic reject.

## Learn from your own channel
When `analytics/results.csv` has about ten videos or more, record which hook shapes performed (see `shorts-analytics`) and add your own channel's shapes to this table. Keep an entry only if at least two videos back it.
