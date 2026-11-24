r"""ytsuggest.py - what people actually type into YouTube search, for titles and tags. No key.

    python tools/ytsuggest.py "how does a zip"         # suggestions for one phrase
    python tools/ytsuggest.py "how does a zip" --expand   # also a..z and question words

Uses YouTube's public autocomplete. It is an unofficial endpoint: if it stops answering, fall back to
WebSearch. Suggestions show demand, not competition. Pick phrases that read naturally in the title.
"""
import json, string, sys, time, urllib.parse, urllib.request

URL = "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q="


def suggest(q):
    req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "replace"))[1]


def main():
    a = [x for x in sys.argv[1:] if x != "--expand"]
    if not a:
        print(__doc__); return
    q, seen = a[0], []
    probes = [q] + ([f"{q} {c}" for c in string.ascii_lowercase] + [f"why {q}", f"how {q}", f"what {q}"]
                    if "--expand" in sys.argv else [])
    for p in probes:
        try:
            for s in suggest(p):
                if s not in seen: seen.append(s)
        except Exception as e:
            print(f"(skipped '{p}': {e})", file=sys.stderr)
        if len(probes) > 1: time.sleep(0.3)
    for s in seen: print(s)


if __name__ == "__main__":
    main()
