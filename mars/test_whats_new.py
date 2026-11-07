#!/usr/bin/env python3
"""What's new on the Mars tracker: show this edition's highlights, omit the block when there are none.

Run from the repo root: python3 mars/test_whats_new.py
"""
import copy, json, os, sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from build import TZ
from build_mars import render_page, select_whats_new

DATA = os.path.join(ROOT, "mars", "data.json")
FIXED = datetime(2026, 11, 7, 5, 0, tzinfo=TZ)
STARSHIP = "targeting Friday, 13 November for Starship Flight 15"
TESLARATI = "https://www.teslarati.com/spacex-starship-catch-nov-13/"

def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)

def block(html):
    i = html.find('id="whats-new"')
    if i < 0:
        return ""
    j = html.find("<h2>Summary", i)
    return html[i:j if j > 0 else None]

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

def main():
    d = load()
    if d.get("updated", "")[:10] != "2026-11-07":
        fail("fixture updated date changed; this test expects the 7 Nov 2026 edition")
    if not select_whats_new(d):
        fail("current data.json should select at least one What's new line")

    html = render_page(d, FIXED)
    b = block(html)
    if not b:
        fail("news condition: What's new section missing")
    if STARSHIP not in b:
        fail("news condition: Starship highlight missing")
    if TESLARATI not in b:
        fail("news condition: Teslarati source link missing")
    if 'href="#feed-' not in b:
        fail("news condition: feed detail link missing")
    if html.find('id="whats-new"') > html.find("<h2>Summary"):
        fail("What's new should sit above the Summary")
    if "Nothing new today" in b:
        fail("daily-check note was promoted into What's new")
    for routine in ("sol 2031", "sol 5066", "only their checked dates change"):
        if routine in b:
            fail("routine check text was promoted: " + routine)
    for heading in ("Summary", "Today and recent, newest first", "Mission status board",
                    "Perseverance counter", "Curiosity", "Plans and company claims",
                    "Upcoming dates", "Terms", "Not read or only partly read"):
        if f"<h2>{heading}</h2>" not in html and f"<h2 id=\"whats-new\">{heading}</h2>" not in html:
            fail("missing section: " + heading)
    # The detail anchor must point at the feed item that cites the same page.
    import re
    m = re.search(r'href="#(feed-\d+)"', b)
    if not m:
        fail("could not read feed anchor")
    anchor = m.group(1)
    if f'id="{anchor}"' not in html or TESLARATI not in html.split(f'id="{anchor}"', 1)[1][:2500]:
        fail("Full note link does not land on the Teslarati feed item")
    print("news condition: ok")

    empty = copy.deepcopy(d)
    empty["whats_new"] = []
    html_empty = render_page(empty, FIXED)
    if 'id="whats-new"' in html_empty or "What's new" in html_empty:
        fail("no-news condition: section still present when whats_new is empty")
    if "<h2>Summary</h2>" not in html_empty:
        fail("no-news condition: Summary missing")
    if "Mission status board" not in html_empty:
        fail("no-news condition: rest of page missing")
    print("no-news condition (empty list): ok")

    stale = copy.deepcopy(d)
    for item in stale["whats_new"]:
        item["edition"] = "2026-11-06"
    html_stale = render_page(stale, FIXED)
    if 'id="whats-new"' in html_stale or "What's new" in html_stale:
        fail("stale edition was carried forward")
    if select_whats_new(stale):
        fail("select_whats_new kept a previous edition")
    print("no-news condition (previous edition left in the list): ok")

    mixed = copy.deepcopy(d)
    mixed["whats_new"] = [
        dict(edition="2026-11-06", text="Old highlight that must not appear.", links=[]),
        dict(edition="2026-11-07", text="   ", links=[]),
        dict(edition="2026-11-07", text="A real line for this edition.", links=[["Source", "https://example.com/mars"]]),
    ]
    chosen = select_whats_new(mixed)
    if len(chosen) != 1 or chosen[0]["text"] != "A real line for this edition.":
        fail("mixed list did not keep only the matching edition: %r" % chosen)
    html_mixed = render_page(mixed, FIXED)
    bm = block(html_mixed)
    if "A real line for this edition." not in bm or "Old highlight" in bm:
        fail("mixed render kept or dropped the wrong line")
    if "example.com/mars" not in bm:
        fail("mixed render dropped the source link")
    print("mixed edition filter: ok")

    missing = copy.deepcopy(d)
    del missing["whats_new"]
    if select_whats_new(missing) or 'id="whats-new"' in render_page(missing, FIXED):
        fail("missing whats_new key should omit the section")
    print("missing key: ok")
    print("all what's-new tests passed")

if __name__ == "__main__":
    main()
