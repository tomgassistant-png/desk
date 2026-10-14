#!/usr/bin/env python3
"""Build yemen/index.html from yemen/items.json. Usage: python3 build_yemen.py"""
import json, os
from datetime import datetime, date
from build import CSS, TZ, e, long_date, weekday_date

NAV_CSS = ('.secnav{text-align:center;font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:.5px;'
           'text-transform:uppercase;border-bottom:1px solid #ccc;padding:6px 0;margin-bottom:6px}'
           '.secnav a{color:#222;text-decoration:none;margin:0 10px}.secnav a.on{font-weight:700;border-bottom:2px solid #222}'
           '.ylede{font-size:20px;font-style:italic;margin:14px 0 18px}.ybox{border-top:1px solid #222;padding-top:8px;margin-top:14px}')

def nav(here, root):
    links = [("jsd", root, "Judea &amp; Samaria"), ("yemen", root + "yemen/", "Yemen"),
             ("bg", root + "#backgrounders", "Backgrounders")]
    return '<nav class="secnav">' + " | ".join(
        f'<a href="{h}"{" class=on" if k == here else ""}>{t}</a>' for k, h, t in links) + '</nav>'

def story(it, h="h3", new=False):
    src = e(it["source"])
    if it.get("link"):
        src = f'<a href="{e(it["link"])}" target="_blank" rel="noopener">{src}</a>'
    cls = "story new" if new else "story"
    tg = '<span class="tag-new">New</span>' if new else ""
    return (f'<article class="{cls}"><{h}>{tg}{e(it["headline"])}</{h}><p class="summary">{e(it["text"])}</p>'
            f'<p class="meta">{src}</p></article>')

def edition(ed, new=False):
    out = [f'<p class="ylede">{e(ed.get("lede",""))}</p><div class="cols">']
    out += [story(it, new=new) for it in ed["items"]]
    out.append('</div>')
    if ed.get("trend"): out.append(f'<div class="ybox"><strong>Trend.</strong> {e(ed["trend"])}</div>')
    if ed.get("watch"): out.append(f'<div class="ybox"><strong>Watch.</strong> {e(ed["watch"])}</div>')
    return "".join(out)

def build(data, now):
    eds = sorted(data["editions"], key=lambda x: x["date"], reverse=True)
    t = data.get("title", "Yemen Desk")
    o = [f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
         '<meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">'
         f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(t)} — {e(long_date(now.date()))}</title>'
         f'<style>{CSS}{NAV_CSS}.story.new h3,.story.new h2{{color:#9b1c1c}}</style></head><body><div class="page">', nav("yemen", "../"),
         f'<div class="topline"><span>Compiled from the daily Yemen campaign brief</span><span>Updated {now:%H:%M} Israel time</span></div>',
         f'<header class="masthead"><h1>{e(t)}</h1><p class="sub">{e(data.get("subtitle",""))}</p></header>']
    if eds:
        top = eds[0]
        o.append(f'<div class="dateline"><span>{e(weekday_date(now.date()))}</span><span>Aden · Sanaa · Riyadh</span>'
                 f'<span>This edition: {e(long_date(top["date"]))}</span></div>')
        o.append(f'<main class="main"><section class="section"><h2>{e(weekday_date(date.fromisoformat(top["date"])))}</h2>{edition(top, new=True)}</section></main>')
    o.append('<section class="archive"><h2>Archive — earlier editions</h2>')
    if len(eds) < 2: o.append('<p class="empty">No earlier editions yet.</p>')
    for ed in eds[1:]:
        o.append(f'<details><summary>{e(weekday_date(date.fromisoformat(ed["date"])))}<span class="n">{len(ed["items"])} items</span></summary>'
                 f'<div class="day">{edition(ed)}</div></details>')
    o.append(f'</section><footer>{e(t)} · {len(eds)} editions on file · built {now:%d %B %Y, %H:%M} Israel time · '
             '<a href="../">Judea &amp; Samaria Desk</a></footer></div></body></html>')
    return "\n".join(o)

if __name__ == "__main__":
    d = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(d, "yemen/items.json"), encoding="utf-8"))
    open(os.path.join(d, "yemen/index.html"), "w", encoding="utf-8").write(build(data, datetime.now(TZ)))
    print(f"wrote yemen/index.html: {len(data['editions'])} editions")
