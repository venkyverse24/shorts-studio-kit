r"""analytics.py - what worked on the channel, and where viewers leave a Short.

    python tools/analytics.py add --name My_Short --title "..." --published 2026-11-23 --length 62 --views 120 --avp 58 --format 3d --topic tech --hook "..."
    python tools/analytics.py report                 # ranking, outlier multiples, patterns
    python tools/analytics.py retention export.csv [--timing my_short/audio/timing.json] [--length 90]

Data lives in analytics/results.csv (plain text, edited by hand or with `add`). Numbers come from the
YouTube Studio pages you export or read out; nothing here logs in to YouTube.
"""
import argparse, csv, os, re, statistics, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "analytics", "results.csv")
COLS = ["name", "title", "published", "length_s", "views", "avg_view_pct", "likes", "comments", "format", "topic", "hook", "source", "notes"]


def load():
    if not os.path.exists(CSV): return []
    with open(CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x):
    try: return float(str(x).replace(",", "").replace("%", ""))
    except ValueError: return None


def add(a):
    os.makedirs(os.path.dirname(CSV), exist_ok=True)
    new = not os.path.exists(CSV)
    row = {c: getattr(a, c, "") or "" for c in COLS}
    with open(CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, COLS)
        if new: w.writeheader()
        w.writerow(row)
    print("added", a.name)


def report(_):
    rows = [r for r in load() if num(r["views"]) is not None]
    if len(rows) < 2:
        print("need at least two rows with views in analytics/results.csv"); return
    views = [num(r["views"]) for r in rows]
    med = statistics.median(views)
    print(f"{len(rows)} videos, median {med:.0f} views\n")
    print(f"{'name':<28}{'views':>8}{'x median':>10}{'avg view %':>12}  format / topic")
    for r in sorted(rows, key=lambda r: -num(r["views"])):
        v = num(r["views"]); p = num(r["avg_view_pct"])
        print(f"{r['name'][:27]:<28}{v:>8.0f}{v / med:>9.1f}x{(f'{p:.0f}' if p is not None else '-'):>12}  {r['format']} / {r['topic']}")
    for key in ("format", "topic"):
        g = defaultdict(list)
        for r in rows:
            if r[key]: g[r[key]].append(num(r["views"]))
        if len(g) > 1:
            print(f"\nby {key} (median views, n):")
            for k, v in sorted(g.items(), key=lambda kv: -statistics.median(kv[1])):
                print(f"  {k:<16}{statistics.median(v):>8.0f}  n={len(v)}")
    print("\nSmall samples: treat patterns as hints for the next test, not conclusions.")


def read_series(path):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        rows = [r for r in csv.reader(f) if r]
    head = rows[0]
    hdr = [h.lower() for h in head]
    t = next((i for i, h in enumerate(hdr) if re.search(r"time|second|position|elapsed|video", h)), None)
    v = next((i for i, h in enumerate(hdr) if re.search(r"retention|watching|audience|viewers|%", h) and i != t), None)
    body = rows[1:]
    if t is None or v is None:
        t, v = 0, 1
    pts = []
    for r in body:
        if len(r) <= max(t, v): continue
        x, y = num(r[t]), num(r[v])
        if x is not None and y is not None: pts.append((x, y))
    return pts, head


def retention(a):
    pts, head = read_series(a.csv)
    if len(pts) < 5:
        sys.exit(f"could not find a time column and a retention column in {a.csv} (header: {head})")
    xs = [p[0] for p in pts]
    length = a.length or (max(xs) if max(xs) > 1.5 else None)
    if max(xs) <= 1.5 and not a.length:
        sys.exit("x values look like a 0-1 fraction of the video: pass --length <seconds>")
    if max(xs) <= 1.5: pts = [(x * a.length, y) for x, y in pts]
    ys = [p[1] for p in pts]
    if max(ys) <= 1.5: pts = [(x, y * 100) for x, y in pts]       # fraction -> percent
    pts.sort()

    def at(sec):
        return min(pts, key=lambda p: abs(p[0] - sec))[1]
    print(f"{len(pts)} points, {pts[-1][0]:.0f} s\n")
    for s in (1, 3, 10, 30):
        if s < pts[-1][0]: print(f"  still watching at {s:>2} s: {at(s):.0f}%")
    print(f"  at the end ({pts[-1][0]:.0f} s): {pts[-1][1]:.0f}%")
    drops = sorted(((pts[i][1] - pts[i + 1][1], pts[i][0], pts[i + 1][0]) for i in range(len(pts) - 1)), reverse=True)[:3]
    print("\nbiggest drops:")
    scenes = []
    if a.timing:
        import json
        t = json.load(open(a.timing, encoding="utf-8"))["scenes"]; cur = 0
        for k, m in t.items(): scenes.append((k, cur, cur + m["dur"])); cur += m["dur"]
    for d, s0, s1 in drops:
        where = next((f" (scene {k})" for k, c0, c1 in scenes if c0 <= s0 < c1), "")
        print(f"  -{d:.1f} points between {s0:.0f} s and {s1:.0f} s{where}")
    first10 = at(10) if pts[-1][0] > 10 else at(pts[-1][0])
    verdict = "hook loses people early: rework the first lines" if at(3 if pts[-1][0] > 3 else 1) < 70 else \
              "hook holds; look at the biggest drop in the body" if first10 >= 50 else "viewers leave in the first ten seconds"
    print(f"\nreading: {verdict}\nThis is a description of one video, not proof of cause: compare against the script at those seconds.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ad = sub.add_parser("add")
    for c in COLS: ad.add_argument("--" + c.replace("_", "-"), dest=c, default="")
    ad.set_defaults(fn=add)
    sub.add_parser("report").set_defaults(fn=report)
    r = sub.add_parser("retention"); r.add_argument("csv"); r.add_argument("--timing"); r.add_argument("--length", type=float)
    r.set_defaults(fn=retention)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
