r"""titlecheck.py - lint a Short's title, thumbnail text and hashtags together.

    python tools/titlecheck.py --title "How Does a Zip Lock Together?" --thumb "BUMP. HOLLOW. LOCKED."
    python tools/titlecheck.py titles.txt            # one title per line

Prints PASS/WARN/FAIL lines and exits 1 if any FAIL.
Optional shorts-kit.json (current folder or the folder above tools/):
  "forbidden"       private terms that must never appear (names, hostnames...)
  "banned_phrases"  channel-specific phrases to refuse in titles
  "allowed_caps"    ALL-CAPS words that are fine (acronyms, brand)
"""
import json, os, re, sys


def load_config():
    for d in (os.getcwd(), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        p = os.path.join(d, "shorts-kit.json")
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))
    return {}


CFG = load_config()
GENERIC_PRIVATE = r"\b\d{1,3}(\.\d{1,3}){3}\b|[\w.+-]+@[\w-]+\.[\w.]+|[A-Za-z]:\\Users\\|/home/\w+"
PRIVATE = re.compile("|".join([GENERIC_PRIVATE] + [re.escape(t) for t in CFG.get("forbidden", []) if t]), re.I)
BANNED = [re.compile(re.escape(p), re.I) for p in CFG.get("banned_phrases", []) if p]
ALLOWED_CAPS = {c.upper() for c in CFG.get("allowed_caps", [])}
CLICKBAIT = re.compile(r"\b(you won'?t believe|shocking|gone wrong|exposed|insane|mind[- ]?blowing|banned|they don'?t want)\b", re.I)
FINANCE = re.compile(r"\b(trading|stock|invest|profit|gold|crypto|returns?)\b", re.I)
PROMISE = re.compile(r"\b(guaranteed|get rich|double your|risk[- ]free|sure profit)\b", re.I)
STOP = {"the", "a", "an", "of", "to", "and", "in", "on", "is", "how", "does", "do", "your", "you", "it"}


def check(title, thumb=None):
    out = []
    add = lambda lvl, msg: out.append((lvl, msg))
    n = len(title)
    add("PASS" if n <= 70 else "WARN", f"title length {n} (aim 70 or less; search shows about 60 on phones)")
    if n > 100: add("FAIL", "title over YouTube's 100 character limit")
    if len(re.findall(r"#\w+", title)) > 3: add("WARN", "more than three hashtags in the title")
    caps = [w for w in re.findall(r"\b[A-Z]{5,}\b", title) if w not in ALLOWED_CAPS]
    if len(caps) > 1: add("WARN", f"shouting: {', '.join(caps)}")
    if CLICKBAIT.search(title): add("FAIL", "clickbait phrase the video cannot back up")
    if PRIVATE.search(title): add("FAIL", "private information in the title")
    for b in BANNED:
        if b.search(title): add("FAIL", f"banned phrase: {b.pattern}")
    if FINANCE.search(title) and PROMISE.search(title): add("FAIL", "profit promise in a finance title")
    if not re.search(r"\?|\bhow\b|\bwhy\b|\bwhat\b|\bsecret\b|\bfrom\b.+\bto\b|\d", title, re.I):
        add("WARN", "no question, number or contrast: the promise may be flat")
    first = title[:40]
    add("PASS" if re.search(r"[A-Za-z]{4,}", first) else "WARN", f"first 40 characters carry the topic: '{first}'")
    if thumb is not None:
        w = thumb.split()
        add("PASS" if len(w) <= 4 else "WARN", f"thumbnail text is {len(w)} words (aim 4 or fewer)")
        if len(thumb) > 28: add("WARN", "thumbnail text longer than 28 characters is hard to read on a phone")
        tw = {x.lower() for x in re.findall(r"\w+", title)} - STOP
        thw = {x.lower() for x in re.findall(r"\w+", thumb)} - STOP
        if thw and thw <= tw: add("WARN", "thumbnail repeats the title; add the puzzle or the number the title does not say")
        if PRIVATE.search(thumb): add("FAIL", "private information on the thumbnail")
    return out


def main():
    a = sys.argv[1:]
    if "--title" in a:
        items = [(a[a.index("--title") + 1], a[a.index("--thumb") + 1] if "--thumb" in a else None)]
    elif a:
        items = [(l.strip(), None) for l in open(a[0], encoding="utf-8") if l.strip()]
    else:
        print(__doc__); return
    bad = False
    for t, th in items:
        print(f"\n  {t}" + (f"   [thumb: {th}]" if th else ""))
        for lvl, msg in check(t, th):
            print(f"    {lvl:<5} {msg}")
            bad |= lvl == "FAIL"
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
