#!/usr/bin/env python3
"""Build yemen/index.html from yemen/items.json. Usage: python3 build_yemen.py"""
import json, os
from datetime import datetime, date
from build import CSS, TZ, e, long_date, weekday_date

NAV_CSS = ('.secnav{text-align:center;font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:.5px;'
           'text-transform:uppercase;border-bottom:1px solid #ccc;padding:6px 0;margin-bottom:6px}'
           '.secnav a{color:#222;text-decoration:none;margin:0 10px}.secnav a.on{font-weight:700;border-bottom:2px solid #222}'
           '.ylede{font-size:20px;font-style:italic;margin:14px 0 18px}.ybox{border-top:1px solid #222;padding-top:8px;margin-top:14px}')


MAP_CSS = ('.ymap{margin:14px 0 18px;border-top:1px solid #222;border-bottom:1px solid #ccc;padding:10px 0}'
           '.ymap h2{margin:0 0 8px}.ymap img{width:100%;height:auto;display:block;border:1px solid #ccc}'
           '.ymap .cap{font-size:13px;color:#444;margin:6px 0 0;font-family:Helvetica,Arial,sans-serif;line-height:1.4}'
           '.ymap .key span{display:inline-block;margin-right:12px}.ymap .sw{display:inline-block;width:12px;height:12px;vertical-align:middle;margin-right:4px;border:1px solid #888}'
           '#ylmap{height:380px;margin-top:12px;border:1px solid #ccc}@media(max-width:700px){#ylmap{height:300px}}')
PLACES = [("Sanaa",15.3694,44.1910,"Houthi-held capital"),("Hodeidah",14.7978,42.9545,"Houthi-held port"),
          ("Marib",15.4543,45.3260,"Government-held city, front to the west"),("Taiz",13.5795,44.0209,"Divided city: government holds the center, Houthis ring it"),
          ("Aden",12.7855,45.0187,"Government seat; STC forces dominant"),("Lahj",13.0567,44.8819,"Government/STC-held, south of the Taiz front"),
          ("Harib",14.9333,45.5000,"Marib province, government-held per map (approx. position)"),
          ("Riyadh",24.7136,46.6753,"Saudi capital, Houthi missile/drone target"),("Khamis Mushait",18.3000,42.7333,"Saudi air base city, Houthi target")]
def map_section():
    import json as _j
    pts = _j.dumps(PLACES)
    return ('<section class="ymap"><h2>Map: who controls what</h2>'
            '<a href="https://commons.wikimedia.org/wiki/File:Yemeni_Civil_War.svg" target="_blank" rel="noopener">'
            '<img src="yemen-control-map.png" alt="Map of territorial control in Yemen" loading="lazy"></a>'
            '<p class="cap key"><span><i class="sw" style="background:#7a9a96"></i>Houthis</span>'
            '<span><i class="sw" style="background:#f9c8c8"></i>Government (Presidential Leadership Council, including STC forces)</span>'
            '<span><i class="sw" style="background:#fff"></i>AQAP</span></p>'
            '<p class="cap">Source: <a href="https://commons.wikimedia.org/wiki/File:Yemeni_Civil_War.svg" target="_blank" rel="noopener">Wikimedia Commons, “Yemeni Civil War.svg”</a> '
            '(Ali Zifan and contributors, CC BY-SA 4.0). Map last updated 14 October 2026 on Commons (Lahj front, citing open-source reports and ISWNews). '
            'Checked 22 October 2026; no newer reusable map found (Commons file history and Critical Threats checked; on 19 October South24, the Anaween Center and SouthFront were also checked, and SouthFront\'s 18 October map is from a pro-Russian outlet and not openly licensed). Front lines are approximate and change often. '
            'Critical Threats reported on 20 October that Houthi and government-aligned forces both hold positions on Jabal Han, the mountain overlooking western Taiz City, with neither controlling the summit despite a Houthi claim to hold all of it, and that government-aligned forces are fighting in al-Misrakh and Sabr al-Madawim south of the city near the Taiz-Aden road. '
            'Critical Threats reported on 21 October that geolocated footage showed government-aligned forces operating in previously Houthi-held territory in Misrakh District south of Taiz City, in an effort to break the Houthi encirclement of central Taiz, and that fighting continued near Murad, south of Dhubab Airport. '
            'Critical Threats reported on 19 October that the Houthis are sending reinforcements to Taiz Governorate and that government-aligned forces have largely repelled recent Houthi advances near Taiz City, and that fighting continues at Jabal Kahbub in Lahij; on 18 October it reported the Old Airport neighborhood on the western edge of Taiz City heavily contested. These claims are unconfirmed and not shown on this map. '
            'Critical Threats reported on 16 October that government-aligned forces had retaken Dhubab Airport on the Red Sea coast by 15 October, after this map was last updated; the Anaween Center\'s provisional assessment of 15 October also shows Dhubab and mainland Bab al-Mandab back under government control, with Mokha still Houthi-held. '
            'It does not separate STC-held areas from other government areas; the STC is strongest in Aden, Lahj and the south. '
            'For a live view see <a href="https://yemen.liveuamap.com/" target="_blank" rel="noopener">Liveuamap Yemen</a> (link only; cannot be embedded).</p>'
            '<div id="ylmap" aria-label="Places in the brief"></div>'
            '<p class="cap">Places named in the brief, including Saudi targets. Base map © OpenStreetMap contributors. Positions are city centers.</p>'
            '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">'
            '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
            '<script>(function(){if(!window.L)return;var m=L.map("ylmap",{scrollWheelZoom:false}).setView([17.5,45],5);'
            'L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:12,attribution:"© OpenStreetMap contributors"}).addTo(m);'
            f'var P={pts};P.forEach(function(p){{L.circleMarker([p[1],p[2]],{{radius:6,color:"#9b1c1c",fillOpacity:.8}}).addTo(m).bindTooltip("<b>"+p[0]+"</b><br>"+p[3]);}});'
            '})();</script></section>')

def nav(here, root):
    links = [("cover", root + "cover/", "Cover"), ("jsd", root, "Judea &amp; Samaria"), ("yemen", root + "yemen/", "Yemen"),
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
         f'<style>{CSS}{NAV_CSS}{MAP_CSS}.story.new h3,.story.new h2{{color:#9b1c1c}}</style></head><body><div class="page">', __import__("sitenav").nav("yemen", "../"),
         f'<div class="topline"><span>Compiled from the daily Yemen campaign brief</span><span>Updated {now:%H:%M} Israel time</span></div>',
         f'<header class="masthead"><h1>{e(t)}</h1><p class="sub">{e(data.get("subtitle",""))}</p></header>']
    if eds:
        top = eds[0]
        o.append(f'<div class="dateline"><span>{e(weekday_date(now.date()))}</span><span>Aden · Sanaa · Riyadh</span>'
                 f'<span>This edition: {e(long_date(top["date"]))}</span></div>')
        o.append(f'<main class="main"><section class="section"><h2>{e(weekday_date(date.fromisoformat(top["date"])))}</h2>{edition(top, new=True)}</section></main>')
        o.append(map_section())
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
