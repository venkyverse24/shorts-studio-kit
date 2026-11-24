r"""hookscore.py - a quick lint for the first lines of a Short.

    python tools/hookscore.py --hook "Your coat zip has no glue and no hooks. So how does it never come apart?"
    python tools/hookscore.py hooks.txt            # one hook per line, best first
    python tools/hookscore.py --examples           # sample hooks, to see how it reads

Six checks from 0 to 100: gap, puzzle, viewer, specific, pace, clean.
The score is the average of the six. If any single check is below 25 the score is capped at 49,
so one dead check cannot hide behind five good ones.
Bands: GOOD 70+, OK 50-69, WEAK below 50.

What it is: a lint. It catches greetings, digits, no question, too long or too short, hype words
and private terms. What it is not: a prediction of views, and not a fact check. A hook can score
high and still make a claim the sources do not back, so always check claims against the research
note first. Picture-led hooks can score low and still work.

Private terms to block come from shorts-kit.json ("forbidden"), found in the current folder or
the folder above tools/. Emails, IP addresses and home-folder paths are always blocked.
"""
import json, os, re, sys

WORDS_PER_SECOND = 2.6          # a calm narrator
IDEAL_SECONDS = (3.5, 8.5)      # the hook should land inside the first few seconds


def load_config():
    for d in (os.getcwd(), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        p = os.path.join(d, "shorts-kit.json")
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))
    return {}


CFG = load_config()
GENERIC_PRIVATE = r"\b\d{1,3}(\.\d{1,3}){3}\b|[\w.+-]+@[\w-]+\.[\w.]+|[A-Za-z]:\\Users\\|/home/\w+"
PRIVATE = re.compile("|".join([GENERIC_PRIVATE] + [re.escape(t) for t in CFG.get("forbidden", []) if t]), re.I)

QUESTION_WORDS = {"how", "why", "what", "which", "who", "where", "when", "whose"}
CONSTRAINT_WORDS = {"no", "never", "nothing", "without", "cannot", "can't", "doesn't", "don't", "isn't", "won't", "not", "yet", "even", "but"}
SECOND_PERSON = {"you", "your", "yours", "yourself", "you're"}
SCENE_PEOPLE = {"man", "woman", "boy", "girl", "driver", "shopper", "child", "someone", "imagine", "picture"}
NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "twenty", "thirty",
                "forty", "fifty", "hundred", "thousand", "million", "billion", "half", "double", "triple"}
UNIT_WORDS = {"second", "seconds", "minute", "minutes", "hour", "hours", "day", "days", "week", "weeks", "year", "years",
              "metre", "metres", "meter", "meters", "kilometre", "kilometres", "gram", "grams", "degree", "degrees", "percent"}
HYPE_WORDS = {"amazing", "incredible", "insane", "crazy", "unbelievable", "epic", "shocking", "legendary", "ultimate", "revolutionary", "mindblowing"}
FILLER_OPENERS = {"hey", "hi", "hello", "welcome", "so", "today", "guys", "everyone", "okay", "ok"}
ASK_FOR_ACTION = re.compile(r"\b(subscribe|like and|follow me|smash)\b", re.I)
CONTRAST = re.compile(r"\bfrom\b.+\bto\b|\bversus\b|\bvs\b|\bturns? into\b|\bbecomes?\b|\bthen and now\b", re.I)


def tokens(text):
    return re.findall(r"[a-z0-9']+", text.lower().replace("’", "'"))


def clamp(x):
    return max(0, min(100, round(x)))


def gap(text, toks):
    asked = sum(1 for t in toks if t in QUESTION_WORDS)
    return clamp(10 + 24 * min(asked, 3) + (24 if text.strip().endswith("?") else 0))


def puzzle(text, toks):
    # a rule that looks impossible, then the question that follows from it
    rules = sum(1 for t in toks if t in CONSTRAINT_WORDS)
    asked = any(t in QUESTION_WORDS for t in toks) or "?" in text
    return clamp(10 + 18 * min(rules, 3) + (26 if rules and asked else 0) + (20 if CONTRAST.search(text) else 0))


def viewer(text, toks):
    you = sum(1 for t in toks if t in SECOND_PERSON)
    person = any(t in SCENE_PEOPLE for t in toks)
    return clamp(20 + 24 * min(you, 2) + (30 if person else 0) + (10 if toks[:5] and any(t in SECOND_PERSON for t in toks[:5]) else 0))


def specific(text, toks):
    concrete = sum(1 for t in toks if t.isdigit() or t in NUMBER_WORDS or t in UNIT_WORDS)
    names = sum(1 for w in text.split()[1:] if w[:1].isupper() and not w.isupper())
    hype = sum(1 for t in toks if t.replace("-", "") in HYPE_WORDS)
    return clamp(35 + 16 * min(concrete, 3) + 7 * min(names, 3) - 22 * hype)


def pace(text, toks):
    secs = len(toks) / WORDS_PER_SECOND
    lo, hi = IDEAL_SECONDS
    if not toks:
        return 0
    off = lo - secs if secs < lo else secs - hi if secs > hi else 0
    return clamp(100 - 18 * off)


def clean(text, toks):
    s = 100
    if toks and toks[0] in FILLER_OPENERS: s -= 55
    if PRIVATE.search(text): s -= 100
    if any(ch.isdigit() for ch in text): s -= 25     # narration should spell numbers as words
    if ASK_FOR_ACTION.search(text): s -= 40
    return max(0, s)


CHECKS = [("gap", gap), ("puzzle", puzzle), ("viewer", viewer), ("specific", specific), ("pace", pace), ("clean", clean)]
HINTS = {"gap": "ask the question the viewer cannot answer yet",
         "puzzle": "state a rule that looks impossible, then ask how",
         "viewer": "put the viewer or a person in the first line",
         "specific": "swap a vague word for a number, a place or a named thing; cut hype words",
         "pace": "aim for about 4 to 8 seconds spoken (roughly 9 to 22 words)",
         "clean": "drop the greeting or subscribe line, spell digits as words, remove private terms"}

EXAMPLES = [
    ("rule + question", "Your coat zip has no glue and no hooks. So how does it never come apart?"),
    ("scene + question", "You stop at a red light and it turns green the moment you arrive. No camera, no switch, nobody watching. How did it know?"),
    ("before and after", "Phone cameras went from this to this in fifteen years. But the sensor is not what changed."),
    ("big claim", "One invention changed how every city is built."),
    ("greeting (bad)", "Hey guys, welcome back, today we talk about 3 amazing facts, subscribe!"),
]


def score(text):
    toks = tokens(text)
    parts = {name: fn(text, toks) for name, fn in CHECKS}
    total = round(sum(parts.values()) / len(parts))
    if min(parts.values()) < 25:
        total = min(total, 49)
    return parts, total


def band(v):
    return "GOOD" if v >= 70 else "OK" if v >= 50 else "WEAK"


def show(label, text):
    parts, total = score(text)
    weakest = min(parts, key=parts.get)
    print(f"\n[{label}] {total} {band(total)}")
    print(f"   \"{text.strip()}\"")
    print("   " + " | ".join(f"{k} {v}" for k, v in parts.items()))
    if parts[weakest] < 70:
        print(f"   improve {weakest}: {HINTS[weakest]}")


def main():
    a = sys.argv[1:]
    if "--examples" in a:
        for label, text in EXAMPLES: show(label, text)
        return
    if "--hook" in a:
        lines = [a[a.index("--hook") + 1]]
    elif a:
        lines = [l for l in open(a[0], encoding="utf-8").read().splitlines() if l.strip()]
    else:
        print(__doc__); return
    ranked = sorted(lines, key=lambda t: -score(t)[1])
    for i, text in enumerate(ranked, 1): show(f"#{i}", text)
    if len(ranked) > 1:
        print(f"\nhighest score: #1 ({score(ranked[0])[1]}). Highest is not the same as best: check every claim against the research note.")


if __name__ == "__main__":
    main()
