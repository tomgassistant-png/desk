#!/usr/bin/env python3
"""Download today's print front pages for the MSM page into msm/frontpages/ and write msm/frontpages/frontpages.json.
Sources: Freedom Forum (cdn.freedomforum.org PDF per day-of-month for the NYT; CloudFront copy for the WSJ) and Paperboy (cdn.thepaperboy.com dated JPEGs for the Guardian and the Financial Times).
Never fails the build: on any error it keeps the images already on disk (the page then labels them with their older date). Always exits 0."""
import os, sys, io, json, subprocess, tempfile, urllib.request
from datetime import datetime, date, timedelta, timezone
from email.utils import parsedate_to_datetime
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Jerusalem")
except Exception:
    TZ = timezone(timedelta(hours=2))
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, "frontpages"); META = os.path.join(OUT, "frontpages.json")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"}
FF = "https://cdn.freedomforum.org/dfp"
CF = "https://d2dr22b2lm4tvw.cloudfront.net"
PB = "https://cdn.thepaperboy.com/frontpages"
# Freedom Forum does not carry the Guardian or the Financial Times (checked 13 Nov 2026; no UK titles in its public list).
PAPERS = [
    dict(key="nyt", name="The New York Times", site="https://www.nytimes.com/", kind="ff", code="NY_NYT"),
    dict(key="wsj", name="The Wall Street Journal", site="https://www.wsj.com/", kind="cf", code="wsj"),
    dict(key="guardian", name="The Guardian", site="https://www.theguardian.com/", kind="pb", code="the_guardian"),
    dict(key="ft", name="Financial Times", site="https://www.ft.com/", kind="pb", code="financial_times"),
]
FULL_W, THUMB_W = 1100, 360
CREDIT = "Front pages via Freedom Forum (frontpages.freedomforum.org) and Paperboy (thepaperboy.com)"

def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers

def save(img, key):
    img = img.convert("RGB")
    full = img.resize((FULL_W, round(img.height * FULL_W / img.width)), Image.LANCZOS) if img.width > FULL_W else img
    th = img.resize((THUMB_W, round(img.height * THUMB_W / img.width)), Image.LANCZOS)
    full.save(os.path.join(OUT, f"{key}.jpg"), quality=76, optimize=True, progressive=True)
    th.save(os.path.join(OUT, f"{key}-thumb.jpg"), quality=78, optimize=True, progressive=True)

def from_pdf(data):
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "a.pdf"); open(p, "wb").write(data)
        subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=90", "-scale-to-x", "1400", "-scale-to-y", "-1", "-singlefile", p, os.path.join(t, "o")], check=True, timeout=90)
        return Image.open(os.path.join(t, "o.jpg")).copy()

def try_ff(p, d):
    """Freedom Forum day-of-month files are reused every month, so check Last-Modified is within a day of d."""
    for kind in ("pdf", "jpg"):
        url = f"{FF}/pdf{d.day}/{p['code']}.pdf" if kind == "pdf" else f"{FF}/jpg{d.day}/lg/{p['code']}.jpg"
        try:
            data, h = get(url)
            lm = parsedate_to_datetime(h["Last-Modified"]).astimezone(timezone.utc).date()
            if abs((lm - d).days) > 1: return None
            img = from_pdf(data) if kind == "pdf" else Image.open(io.BytesIO(data))
            return img, url, h["Last-Modified"]
        except Exception as ex:
            print(f"  {p['key']} {kind} {d}: {ex}")
    return None

def try_cf(p, d):
    url = f"{CF}/{p['code']}/{d.isoformat()}/front-page-large.jpg"
    try:
        data, h = get(url)
        return Image.open(io.BytesIO(data)), url, h.get("Last-Modified", "")
    except Exception as ex:
        print(f"  {p['key']} {d}: {ex}"); return None

def try_pb(p, d):
    """Paperboy paths include the edition date, so a 200 response is that day's page. Prefer the large file."""
    for suffix in (f"{p['code']}_lg.jpg", f"{p['code']}.jpg"):
        url = f"{PB}/uk/{d.strftime('%Y%m%d')}/{suffix}"
        try:
            data, h = get(url)
            return Image.open(io.BytesIO(data)), url, h.get("Last-Modified", "")
        except Exception as ex:
            print(f"  {p['key']} {suffix} {d}: {ex}")
    return None

FETCH = {"ff": try_ff, "cf": try_cf, "pb": try_pb}
SOURCE = {"ff": "Freedom Forum", "cf": "Freedom Forum", "pb": "Paperboy"}

def main():
    os.makedirs(OUT, exist_ok=True)
    try: old = {x["key"]: x for x in json.load(open(META))["papers"]}
    except Exception: old = {}
    today = datetime.now(TZ).date(); papers = []
    for p in PAPERS:
        rec = dict(old.get(p["key"], {})); rec.update(key=p["key"], name=p["name"], site=p["site"])
        try:
            have = rec.get("edition") if os.path.exists(os.path.join(OUT, p["key"] + ".jpg")) else None
            got = False
            if have != today.isoformat():
                for off in (0, 1, 2):
                    d = today - timedelta(days=off)
                    if have and d.isoformat() <= have: break  # nothing newer to look for
                    r = FETCH[p["kind"]](p, d)
                    if r:
                        img, url, lm = r; save(img, p["key"])
                        rec.update(edition=d.isoformat(), source=SOURCE[p["kind"]], source_url=url, last_modified=lm, fetched=datetime.now(TZ).isoformat(timespec="seconds"),
                                   file=f"frontpages/{p['key']}.jpg", thumb=f"frontpages/{p['key']}-thumb.jpg")
                        print(f"{p['key']}: edition {d} OK"); got = True; break
            if not got: print(f"{p['key']}: nothing new, keeping {rec.get('edition')}")
        except Exception as ex:
            print(f"{p['key']}: error {ex}, keeping {rec.get('edition')}")
        if rec.get("file") and os.path.exists(os.path.join(OUT, p["key"] + ".jpg")): papers.append(rec)
    json.dump(dict(updated=datetime.now(TZ).isoformat(timespec="seconds"), credit=CREDIT, papers=papers), open(META, "w"), indent=1, ensure_ascii=False)
    print("wrote", META, [x["key"] + ":" + x.get("edition", "?") for x in papers])

if __name__ == "__main__":
    try: main()
    except Exception as ex: print("fetch_frontpages failed:", ex)
    sys.exit(0)
