#!/usr/bin/env python3
"""Build the personal cover page (cover/) and the digest section pages (digest/<section>/).
Reads digest/items.json, plus items.json (JSD) and yemen/items.json for the 'new today' lines.
Run: python3 build_cover.py"""
import json, os
import sitenav
from datetime import datetime
from build import CSS, NAV_CSS, JS, TZ, e, long_date, weekday_date, weather_html

ROOT = os.path.dirname(os.path.abspath(__file__))
ROBOTS = ('<meta name="robots" content="noindex, nofollow, noarchive">'
          '<meta name="googlebot" content="noindex, nofollow, noarchive">')
EXTRA = ('.story.new h3 a{color:#9b1c1c}.cov-list{list-style:none;padding:0;font-family:Helvetica,Arial,sans-serif;font-size:14px}'
         '.cov-list li{margin:0 0 9px;line-height:1.4}.cov-list li b{display:inline-block;min-width:0;margin-right:6px}'
         '.cov-list li.quiet{color:#777}.secnav{flex-wrap:wrap;line-height:2}.srcs{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555}'
         '.cov-grid{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:36px}@media(max-width:820px){.cov-grid{grid-template-columns:1fr}}'
         'h2.edn{font-family:Helvetica,Arial,sans-serif;font-size:13px;text-transform:uppercase;letter-spacing:1px;border-top:1px solid #ccc;padding-top:8px;margin-top:26px}')

def load(p, default=None):
    p = os.path.join(ROOT, p)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default

def nav(d, here, root):
    links = [("cover", root + "cover/", "Cover"), ("jsd", root, "Judea &amp; Samaria"), ("yemen", root + "yemen/", "Yemen")]
    links += [(s["id"], f'{root}digest/{s["id"]}/', e(s["name"])) for s in d["sections"]]
    return '<nav class="secnav">' + " | ".join(
        f'<a href="{h}"{" class=on" if k == here else ""}>{t}</a>' for k, h, t in links) + '</nav>'

def head(title):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">{ROBOTS}'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(title)}</title><style>{CSS}{NAV_CSS}{EXTRA}</style></head><body><div class="page">')

def story(it, newest, h="h3"):
    new = it["edition"] == newest
    tag = '<span class="tag-new">New</span>' if new else ""
    url = it["sources"][0]["url"] if it.get("sources") else "#"
    srcs = " · ".join(f'<a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s["name"])}</a>' for s in it.get("sources", []))
    return (f'<article class="story{" new" if new else ""}" id="{e(it["id"])}"><{h}><a href="{e(url)}" rel="noopener" target="_blank">{tag}{e(it["headline"])}</a></{h}>'
            f'<p class="summary">{e(it["text"])}</p><p class="meta srcs">{e(long_date(it["edition"]))} edition · {srcs}</p></article>')

def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(html)

def main():
    d = load("digest/items.json")
    items = d["items"]
    ids = {s["id"] for s in d["sections"]}
    bad = [i["id"] for i in items if i["section"] not in ids or not all(i.get(k) for k in ("id", "edition", "headline", "text"))]
    if bad: raise SystemExit(f"digest/items.json problems: {bad}")
    newest = max(i["edition"] for i in items)
    ed = d.get("editions", {}).get(newest, {})
    now = datetime.now(TZ)
    names = {s["id"]: s["name"] for s in d["sections"]}

    # 'new today' lines
    lines = []
    jsd = load("items.json", {}).get("items", [])
    if jsd:
        jn = max(i["edition"] for i in jsd); top = [i for i in jsd if i["edition"] == jn][0]
        lines.append(f'<li><b>Judea &amp; Samaria</b> <a href="../#{e(top["id"])}">{e(top["headline"])}</a> <span class="srcs">({e(long_date(jn))})</span></li>')
    ye = load("yemen/items.json", {}).get("editions", [])
    if ye:
        y = max(ye, key=lambda x: x["date"]); hl = y["items"][0]["headline"] if y.get("items") else y.get("lede", "")
        lines.append(f'<li><b>Yemen</b> <a href="../yemen/">{e(hl)}</a> <span class="srcs">({e(long_date(y["date"]))})</span></li>')
    for s in d["sections"]:
        todays = [i for i in items if i["section"] == s["id"] and i["edition"] == newest]
        if todays:
            lines.append(f'<li><b>{e(s["name"])}</b> <a href="../digest/{s["id"]}/#{e(todays[0]["id"])}">{e(todays[0]["headline"])}</a></li>')
        else:
            lines.append(f'<li class="quiet"><b>{e(s["name"])}</b> <a href="../digest/{s["id"]}/">Nothing new today</a></li>')

    # cover: top story of each section in today's edition
    seen, top = set(), []
    for i in items:
        if i["edition"] == newest and i["section"] not in seen:
            seen.add(i["section"]); top.append(i)
    body = "".join(f'<p class="sec">{e(names[i["section"]])}</p>' + story(i, newest, "h2") for i in top)
    cover = (head("Tom's Cover — " + long_date(newest)) + sitenav.nav("cover", "../") +
             f'<header class="masthead"><h1>Tom\'s Cover</h1><p class="dateline">{e(weekday_date(now.date()))} · Digest edition of {e(long_date(newest))}</p></header>'
             + (f'<p class="summary"><i>{e(ed["intro"])}</i></p>' if ed.get("intro") else "") +
             f'<div class="cov-grid"><main><h2 class="edn">Top stories</h2>{body}'
             + (f'<p class="srcs">{e(ed["quiet"])}</p>' if ed.get("quiet") else "") +
             f'</main><aside class="rail">{weather_html(d)}<h2 class="edn">New today, by section</h2><ul class="cov-list">{"".join(lines)}</ul></aside></div>'
             f'<p class="srcs">Built {e(now.strftime("%Y-%m-%d %H:%M"))} Israel time from the daily research digest.</p></div><script>{JS}</script></body></html>')
    write(os.path.join(ROOT, "cover/index.html"), cover)

    # section pages with archive by edition
    for s in d["sections"]:
        mine = sorted((i for i in items if i["section"] == s["id"]), key=lambda i: i["edition"], reverse=True)
        out = [head(s["name"] + " — Digest section"), sitenav.nav(s["id"], "../../"),
               f'<header class="masthead"><h1>{e(s["name"])}</h1><p class="dateline">Daily research digest section · latest edition {e(long_date(newest))}</p></header>']
        if s.get("links"):
            out.append('<p class="summary">' + " · ".join(f'<a href="{e(l["url"])}">{e(l["label"])}</a>' for l in s["links"]) + '</p>')
        if not mine:
            out.append(f'<p class="summary">{e(s.get("placeholder") or "No stories in this section yet. The digest reports on it only when there is material news.")}</p>')
        last = None
        for i in mine:
            if i["edition"] != last:
                last = i["edition"]; out.append(f'<h2 class="edn">{e(long_date(last))}{" · today" if last == newest else ""}</h2>')
            out.append(story(i, newest))
        out.append('</div></body></html>')
        write(os.path.join(ROOT, f'digest/{s["id"]}/index.html'), "".join(out))
    print(f"cover + {len(d['sections'])} sections built; edition {newest}, {len(items)} items")

if __name__ == "__main__":
    main()
