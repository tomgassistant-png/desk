#!/usr/bin/env python3
"""Render items.json into a self-contained index.html (broadsheet front page).

Usage:  python3 build.py [--data items.json] [--out index.html] [--now 2026-10-09T07:45]
"""
import argparse, html, json, sys
from collections import OrderedDict
from datetime import datetime, date
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Jerusalem")
SECTIONS = OrderedDict([
    ("pa", "Palestinian Authority Forces and the Threat"),
    ("attacks", "Attacks and Incidents"),
    ("land", "Settlement and Land"),
    ("idf", "IDF and Government Decisions"),
    ("negev", "Negev and Galilee"),
])
REQUIRED = ["id", "edition", "published", "section", "headline", "summary", "source", "date", "url"]

e = lambda s: html.escape(str(s), quote=True)

def long_date(d):
    if isinstance(d, str):
        d = date.fromisoformat(d[:10])
    return f"{d.day} {d.strftime('%B %Y')}"

def weekday_date(d):
    return f"{d.strftime('%A')}, {long_date(d)}"

def validate(items):
    seen, problems = set(), []
    for i, it in enumerate(items):
        for k in REQUIRED:
            if not it.get(k):
                problems.append(f"item {i} ({it.get('id')}): missing '{k}'")
        if it.get("section") not in SECTIONS:
            problems.append(f"item {it.get('id')}: unknown section '{it.get('section')}'")
        if it.get("id") in seen:
            problems.append(f"duplicate id {it.get('id')}")
        seen.add(it.get("id"))
    if problems:
        sys.exit("items.json problems:\n  " + "\n  ".join(problems))

def pub(it):
    return datetime.fromisoformat(it["published"]).astimezone(TZ)

def meta(it, link_text="Source"):
    return (f'<p class="meta"><span class="src">{e(it["source"])}</span> · '
            f'<time datetime="{e(it["date"])}">{e(long_date(it["date"]))}</time> · '
            f'<a href="{e(it["url"])}" rel="noopener" target="_blank">{link_text}</a></p>')

def article(it, cls="story"):
    return (f'<article class="{cls}" id="{e(it["id"])}">'
            f'<h3><a href="{e(it["url"])}" rel="noopener" target="_blank">{e(it["headline"])}</a></h3>'
            f'<p class="summary">{e(it["summary"])}</p>{meta(it)}</article>')

CSS = r"""
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#f4f1ea;color:#1a1a1a;font-family:Georgia,"Times New Roman","Noto Serif","Source Serif Pro",serif;line-height:1.45}
a{color:inherit;text-decoration:none}
a:hover,a:focus{text-decoration:underline}
.page{max-width:1240px;margin:0 auto;padding:18px 28px 40px;background:#fbf9f4;box-shadow:0 0 0 1px #e2ddd1}
.topline{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:13px;font-style:italic;color:#444;border-bottom:1px solid #1a1a1a;padding-bottom:6px}
.masthead{text-align:center;padding:14px 0 6px}
.masthead h1{margin:0;font-size:68px;line-height:1.02;font-weight:700;letter-spacing:.5px;font-family:"Noto Serif Display","Playfair Display",Georgia,serif}
.masthead .sub{margin:6px 0 0;font-size:15px;font-style:italic;color:#333}
.dateline{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;border-top:3px double #1a1a1a;border-bottom:1px solid #1a1a1a;margin-top:12px;padding:6px 2px;font-size:13px;text-transform:uppercase;letter-spacing:1.2px}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:0;margin-top:18px}
.main{padding-right:24px;border-right:1px solid #bdb6a6}
.rail{padding-left:22px}
.lead{border-bottom:2px solid #1a1a1a;padding-bottom:18px;margin-bottom:6px}
.lead .kicker,.kicker{font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;color:#7a1f1f;margin:0 0 6px}
.lead h2{font-size:42px;line-height:1.08;margin:0 0 12px;font-weight:700}
.lead .summary{font-size:19px;line-height:1.5;margin:0 0 8px;columns:2;column-gap:28px;column-rule:1px solid #d3cdbf}
.meta{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555;margin:6px 0 0}
.meta .src{font-weight:700;color:#333}
.meta a{color:#7a1f1f;text-decoration:underline}
.section{margin-top:22px}
.section>h2{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:2px;text-transform:uppercase;margin:0 0 10px;padding:6px 0 5px;border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a}
.section .note{font-size:12px;font-style:italic;color:#555;margin:-4px 0 10px}
.cols{columns:2;column-gap:28px;column-rule:1px solid #d3cdbf}
.story{break-inside:avoid;padding:0 0 14px;margin:0 0 14px;border-bottom:1px solid #d3cdbf}
.story h3{font-size:21px;line-height:1.2;margin:0 0 6px}
.story .summary{margin:0;font-size:15.5px;text-align:justify;hyphens:auto}
.story.first h3{font-size:25px}
.empty{font-style:italic;color:#666;font-size:14px}
.rail h2{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:2px;text-transform:uppercase;margin:0 0 10px;padding:6px 0 5px;border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a}
.rail ol{list-style:none;margin:0;padding:0}
.rail li{padding:9px 0;border-bottom:1px dotted #9d968a}
.rail li .time{display:block;font-family:Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:#7a1f1f}
.rail li a.h{font-size:16px;line-height:1.25;font-weight:700}
.rail li .s{display:block;font-size:12px;color:#555;font-style:italic;margin-top:2px}
.latest-mobile{display:none;margin:4px 0 8px}
.latest-mobile h2{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:2px;text-transform:uppercase;margin:0 0 6px;padding:6px 0 5px;border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a}
.latest-mobile ol{list-style:none;margin:0;padding:0}
.latest-mobile li{padding:8px 0;border-bottom:1px dotted #9d968a}
.latest-mobile li .time{display:block;font-family:Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:#7a1f1f}
.latest-mobile li a.h{font-size:16px;line-height:1.25;font-weight:700}
.latest-mobile li .s{display:block;font-size:12px;color:#555;font-style:italic}
.rail .saved{margin-bottom:22px}
.rail .saved .empty{margin:4px 0 0}
.rail .about{margin-top:22px;font-size:13px;color:#444;border-top:1px solid #1a1a1a;padding-top:10px}
.archive{margin-top:34px;border-top:3px double #1a1a1a;padding-top:6px}
.archive>h2{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:2px;text-transform:uppercase;margin:4px 0 12px}
.archive details{border-bottom:1px solid #bdb6a6;padding:8px 0}
.archive summary{cursor:pointer;font-size:19px;font-weight:700;list-style-position:outside}
.archive summary .n{font-weight:400;font-size:13px;color:#555;font-style:italic;margin-left:8px}
.archive .day{columns:3;column-gap:24px;column-rule:1px solid #d3cdbf;margin-top:10px}
.archive .day .story h3{font-size:16.5px}
.archive .day .story .summary{font-size:14px}
.archive .day .story .sec{font-family:Helvetica,Arial,sans-serif;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:#7a1f1f;margin:0 0 3px}
.highlights{margin-top:34px;border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a;padding:6px 0 8px}
.highlights h2{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:2px;text-transform:uppercase;margin:0 0 6px}
.highlights ul{margin:0;padding:0;list-style:none}
.highlights li{padding:5px 0;border-bottom:1px dotted #9d968a;font-size:16px;line-height:1.3}
.highlights li a{font-weight:700}
.highlights .d{font-family:Helvetica,Arial,sans-serif;font-size:11px;color:#555;white-space:nowrap}
.highlights .note{font-size:12px;font-style:italic;color:#555;margin:6px 0 0}
footer{margin-top:28px;border-top:1px solid #1a1a1a;padding-top:8px;font-size:12px;color:#555;text-align:center;font-style:italic}
@media (max-width:980px){
 .layout{grid-template-columns:1fr}
 .main{padding-right:0;border-right:none}
 .rail{padding-left:0;margin-top:26px}
 .rail .latest-full{display:none}
 .latest-mobile{display:block!important}
 .archive .day{columns:2}
}
@media (max-width:640px){
 .page{padding:10px 14px 28px}
 .masthead h1{font-size:38px}
 .masthead .sub{font-size:13px}
 .dateline{font-size:11px;letter-spacing:.6px}
 .lead h2{font-size:29px}
 .lead .summary{columns:1;font-size:17px}
 .cols,.archive .day{columns:1}
 .story h3,.story.first h3{font-size:20px}
 .story .summary{text-align:left}
}
"""

def build(data, now):
    items = data["items"]
    validate(items)
    n_front = 1
    n_hl = int(data.get("highlight_count", 8))
    n_latest = int(data.get("latest_count", 8))
    order = {it["id"]: i for i, it in enumerate(items)}
    editions = sorted({it["edition"] for it in items}, reverse=True)
    front_ed = set(editions[:n_front])
    front = [it for it in items if it["edition"] in front_ed]
    by_new = lambda xs: sorted(xs, key=lambda it: (pub(it), -order[it["id"]]), reverse=True)

    lead = next((it for it in by_new(front) if it.get("lead")), None) or \
           next((it for it in by_new(front) if it["section"] == "pa"), by_new(front)[0])

    def latest_list(n):
        parts = ['<ol>']
        for it in by_new(front)[:n]:
            t = pub(it)
            parts.append(f'<li><span class="time">{t.day} {t:%b} · {t:%H:%M}</span>'
                         f'<a class="h" href="#{e(it["id"])}">{e(it["headline"])}</a>'
                         f'<span class="s">{e(it["source"])}</span></li>')
        parts.append('</ol>')
        return "".join(parts)

    title = data.get("title", "Judea & Samaria Desk")
    sub = data.get("subtitle", "")
    out = []
    out.append(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
               f'<meta name="robots" content="noindex, nofollow, noarchive"><meta name="viewport" content="width=device-width, initial-scale=1">'
               f'<title>{e(title)} — {e(long_date(now.date()))}</title>'
               f'<meta name="description" content="{e(sub)}"><style>{CSS}</style></head><body><div class="page">')
    out.append(f'<div class="topline"><span>Compiled from the daily PA security letters</span>'
               f'<span>Updated {now:%H:%M} Israel time</span></div>')
    out.append(f'<header class="masthead"><h1>{e(title)}</h1><p class="sub">{e(sub)}</p></header>')
    span = long_date(editions[0]) if editions else ''
    out.append(f'<div class="dateline"><span>{e(weekday_date(now.date()))}</span>'
               f'<span>Jerusalem</span><span>This edition: {e(span)}</span></div>')

    out.append('<div class="layout"><main class="main">')
    out.append(f'<section class="lead" id="{e(lead["id"])}"><p class="kicker">{e(SECTIONS[lead["section"]])}</p>'
               f'<h2><a href="{e(lead["url"])}" rel="noopener" target="_blank">{e(lead["headline"])}</a></h2>'
               f'<p class="summary">{e(lead["summary"])}</p>{meta(lead, "Read the source")}</section>')

    older = [d for d in editions if d not in front_ed]
    marked, fallback = [], []
    for d in older:
        day = [it for it in by_new(items) if it["edition"] == d]
        m = [it for it in day if it.get("highlight")]
        marked += m
        if not m:
            fallback += sorted(day, key=lambda it: (not it.get("lead"), it["section"] != "pa"))[:2]
    keep = {it["id"] for it in (marked + fallback)[:n_hl]}  # marked stories take priority
    hl = [it for it in by_new(items) if it["id"] in keep]
    hl.sort(key=lambda it: it["edition"], reverse=True)
    hl_html = []
    if hl:
        hl_html.append('<section class="highlights"><h2>Highlights from previous editions</h2><ul>')
        for it in hl:
            hl_html.append(f'<li><a href="{e(it["url"])}" rel="noopener" target="_blank">{e(it["headline"])}</a>'
                       f' <span class="d">{e(it["source"])} · {e(long_date(it["edition"]))} edition</span></li>')
        hl_html.append('</ul><p class="note">Full stories are in the archive below.</p></section>')

    out.append('<div class="latest-mobile"><h2>Latest</h2>' + latest_list(5) + '</div>')

    for key, name in SECTIONS.items():
        sec = [it for it in by_new(front) if it["section"] == key and it is not lead]
        if not sec:
            continue
        out.append(f'<section class="section" id="sec-{key}"><h2>{e(name)}</h2>')
        if key == "land":
            out.append('<p class="note">New and restored communities, approvals, land orders and roads, '
                       'including facts reported by critical outlets.</p>')
        out.append('<div class="cols">')
        for j, it in enumerate(sec):
            out.append(article(it, "story first" if j == 0 else "story"))
        out.append('</div></section>')
    out.append('</main>')

    saved = sorted([it for it in items if it.get("saved")], key=lambda it: (it.get("saved_on") or it["date"]), reverse=True)
    sv = ['<div class="saved"><h2>Saved stories</h2>']
    if not saved:
        sv.append('<p class="empty">No saved stories yet.</p>')
    else:
        sv.append('<ol>')
        for it in saved:
            sv.append(f'<li><a class="h" href="{e(it["url"])}" rel="noopener" target="_blank">{e(it["headline"])}</a>'
                      f'<span class="s">{e(it["source"])} · {e(long_date(it["date"]))}</span></li>')
        sv.append('</ol>')
    sv.append('</div>')
    out.append('<aside class="rail">' + "".join(sv) + '<div class="latest-full"><h2>Latest</h2>' + latest_list(n_latest) + '</div><div class="about"><strong>About this page.</strong> Every item is taken from the morning '
               'letters and evening supplements on the Palestinian Authority and security, and links to its '
               'original source. Times are Israel time.</div></aside></div>')

    out.extend(hl_html)
    out.append('<section class="archive"><h2>Archive — earlier editions</h2>')
    if not older:
        out.append('<p class="empty">No earlier days yet.</p>')
    for i, d in enumerate(older):
        day = [it for it in items if it["edition"] == d]
        day.sort(key=lambda it: (list(SECTIONS).index(it["section"]), order[it["id"]]))
        out.append(f'<details><summary>{e(weekday_date(date.fromisoformat(d)))}'
                   f'<span class="n">{len(day)} items</span></summary><div class="day">')
        for it in day:
            out.append(f'<article class="story" id="{e(it["id"])}"><p class="sec">{e(SECTIONS[it["section"]])}</p>'
                       f'<h3><a href="{e(it["url"])}" rel="noopener" target="_blank">{e(it["headline"])}</a></h3>'
                       f'<p class="summary">{e(it["summary"])}</p>{meta(it)}</article>')
        out.append('</div></details>')
    out.append('</section>')
    out.append(f'<footer>{e(title)} · {len(items)} items on file · built {now:%d %B %Y, %H:%M} Israel time</footer>')
    out.append('</div></body></html>')
    return "\n".join(out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="items.json")
    ap.add_argument("--out", default="index.html")
    ap.add_argument("--now", help="override build time (Israel time), e.g. 2026-10-09T07:45")
    a = ap.parse_args()
    now = datetime.fromisoformat(a.now).replace(tzinfo=TZ) if a.now else datetime.now(TZ)
    data = json.load(open(a.data, encoding="utf-8"))
    open(a.out, "w", encoding="utf-8").write(build(data, now))
    print(f"wrote {a.out}: {len(data['items'])} items")
