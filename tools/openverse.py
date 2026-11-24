r"""Openverse search + download with an attribution log. Standard library only, no key.

    python tools/openverse.py search audio "door closing" [--n 8]
    python tools/openverse.py search images "city street" [--n 8]
    python tools/openverse.py get audio <id> --dir assets/sfx/my_short --log my_short/publish/attribution.json

Default licences are cc0, pdm and by (credit only). Share-alike, non-commercial and no-derivatives are left out.
"""
import argparse, json, os, sys, urllib.parse, urllib.request

BASE = "https://api.openverse.org/v1"
UA = "shorts-studio-kit/1.0"
LICENSES = "cc0,pdm,by"


def call(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search(kind, q, n, licenses):
    qs = urllib.parse.urlencode({"q": q, "license": licenses, "license_type": "commercial,modification",
                                 "page_size": n, "mature": "false"})
    return call(f"{BASE}/{kind}/?{qs}")["results"]


def brief(r):
    return {"id": r["id"], "title": r.get("title"), "creator": r.get("creator"), "license": r.get("license"),
            "version": r.get("license_version"), "type": r.get("filetype"), "sec": (r.get("duration") or 0) / 1000,
            "from": r.get("foreign_landing_url")}


def credit(r):
    if r.get("attribution"):
        return r["attribution"]
    lic = f'{r.get("license", "").upper()} {r.get("license_version", "")}'.strip()
    return f'"{r.get("title")}" by {r.get("creator") or "unknown"} ({r.get("foreign_landing_url")}), {lic}'


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("kind", choices=["audio", "images"]); s.add_argument("q")
    s.add_argument("--n", type=int, default=8); s.add_argument("--license", default=LICENSES)
    g = sub.add_parser("get"); g.add_argument("kind", choices=["audio", "images"]); g.add_argument("id")
    g.add_argument("--dir", required=True); g.add_argument("--log", required=True)
    a = ap.parse_args()

    if a.cmd == "search":
        for r in search(a.kind, a.q, a.n, a.license):
            print(json.dumps(brief(r), ensure_ascii=False))
        return
    r = call(f"{BASE}/{a.kind}/{a.id}/")
    if r.get("license") not in LICENSES.split(","):
        sys.exit(f"licence {r.get('license')} is not allowed by default")
    os.makedirs(a.dir, exist_ok=True)
    ext = r.get("filetype") or os.path.splitext(urllib.parse.urlparse(r["url"]).path)[1].lstrip(".") or "bin"
    dst = os.path.join(a.dir, f"{a.id}.{ext}")
    req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dst, "wb") as fh:
        fh.write(resp.read())
    log = json.load(open(a.log, encoding="utf-8")) if os.path.exists(a.log) else []
    log.append({"file": dst, "id": a.id, "title": r.get("title"), "creator": r.get("creator"),
                "license": r.get("license"), "version": r.get("license_version"),
                "source_page": r.get("foreign_landing_url"), "credit": credit(r)})
    os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
    json.dump(log, open(a.log, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(dst, "|", credit(r))


if __name__ == "__main__":
    main()
