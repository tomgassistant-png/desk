#!/usr/bin/env python3
"""Build msm/index.html (today's MSM edition) and msm/archive/YYYY-MM-DD.html (older editions) from msm/data.json.
The MSM page shows what big mainstream newsrooms lead with and what their readers are reading. Daily instructions: prompts/msm.md."""
import os, json, html, sitenav
from datetime import datetime, date
from build import CSS, TZ
D = os.path.dirname(os.path.abspath(__file__))
e = lambda s: html.escape(str(s or ""), quote=True)
EXTRA = (".msm-sec{margin-top:26px}.msm-sec>h2{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:2px;text-transform:uppercase;margin:0 0 10px;padding:6px 0 5px;border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a}"
         ".msm-sec .note{font-size:13px;font-style:italic;color:#555;margin:-2px 0 10px}"
         ".msm-item{padding:0 0 10px;margin:0 0 10px;border-bottom:1px solid #d3cdbf;break-inside:avoid}.msm-item h3{font-size:19px;line-height:1.22;margin:0 0 4px}"
         ".msm-item p{margin:0;font-size:15.5px}.msm-item .ranks{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#7a1f1f;margin-top:4px}"
         ".msm-item .also{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555;margin-top:3px}.msm-item .also a{text-decoration:underline}"
         ".src{font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#555;margin-right:6px}"
         ".op{font-family:Helvetica,Arial,sans-serif;font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#fbf9f4;background:#555;padding:1px 5px 0;margin-right:6px;vertical-align:2px}"
         ".mr-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}.mr-grid h4,.ob h4{font-family:Helvetica,Arial,sans-serif;font-size:12px;letter-spacing:1.2px;text-transform:uppercase;color:#7a1f1f;margin:0 0 4px}"
         ".mr-grid ol,.ob ol{margin:0;padding-left:20px}.mr-grid li,.ob li{font-size:15px;line-height:1.3;padding:3px 0}.mr-grid li a,.ob li a{font-weight:700}"
         ".mr-grid .lst{font-size:12px;font-style:italic;color:#555;margin:0 0 4px}.ob{margin:0 0 16px;padding-bottom:10px;border-bottom:1px dotted #9d968a}.ob p{margin:0 0 6px;font-size:15px}"
         ".msm-cols{columns:2;column-gap:28px;column-rule:1px solid #d3cdbf}@media(max-width:760px){.msm-cols{columns:1}.masthead h1{font-size:46px}}"
         ".fp{margin:18px 0 0}.fp-row{display:flex;gap:12px;overflow-x:auto;padding-bottom:4px}.fp-i{flex:1 1 0;min-width:112px;max-width:200px;margin:0;text-align:center}"
         ".fp-i button{display:block;width:100%;padding:0;border:1px solid #1a1a1a;background:#fff;cursor:zoom-in;box-shadow:0 1px 4px rgba(0,0,0,.2)}.fp-i img{display:block;width:100%;height:auto}"
         ".fp-i figcaption{font-family:Helvetica,Arial,sans-serif;font-size:11px;line-height:1.3;margin-top:5px;color:#333}.fp-i figcaption b{display:block;letter-spacing:.8px;text-transform:uppercase;font-size:10.5px}"
         "@media(max-width:600px){.fp-row{display:grid;grid-template-columns:1fr 1fr;gap:14px 12px}.fp-i{max-width:none}}.fp-i .old{color:#7a1f1f}.fp-credit{font-family:Helvetica,Arial,sans-serif;font-size:11px;color:#555;margin:6px 0 0}"
         "#fp-box{position:fixed;inset:0;z-index:99;background:rgba(0,0,0,.88);display:none;overflow:auto;-webkit-overflow-scrolling:touch;cursor:zoom-out;text-align:center;padding:14px 10px 30px}#fp-box.on{display:block}"
         "#fp-box img{max-width:min(100%,1000px);height:auto;background:#fff;box-shadow:0 2px 14px #000}#fp-box p{font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#eee;margin:10px 0 0}#fp-box a{color:#fff;text-decoration:underline}\n"
         ".msm-foot{font-size:13px;color:#444;margin-top:24px;border-top:1px solid #1a1a1a;padding-top:8px}.msm-foot li{margin:2px 0}")

def long_date(s):
    d = date.fromisoformat(s); return f"{d:%A}, {d.day} {d:%B %Y}"

def a(u, t):
    return f'<a href="{e(u)}" target="_blank" rel="noopener">{e(t)}</a>'

def item(i, ranks=True):
    op = '<span class="op">Opinion</span>' if i.get("opinion") else ""
    also = ""
    if i.get("also"):
        also = '<p class="also">Also: ' + " · ".join(a(x["url"], x["outlet"]) for x in i["also"]) + "</p>"
    rk = f'<p class="ranks">{e(i["ranks"])}</p>' if ranks and i.get("ranks") else ""
    sec = f'{e(i["section"])} · ' if i.get("section") else ""
    return (f'<div class="msm-item"><h3>{op}{a(i["url"], i["headline"])}</h3>'
            f'<p><span class="src">{sec}{e(i.get("outlet",""))}</span>{e(i.get("text",""))}</p>{rk}{also}</div>')

def frontpages_html(ed):
    """Row of print front pages (msm/frontpages/frontpages.json, written by msm/fetch_frontpages.py). Empty if the file is missing."""
    try: fp = json.load(open(os.path.join(D, "msm/frontpages/frontpages.json"), encoding="utf-8"))
    except Exception: return ""
    figs = []
    for p in fp.get("papers", []):
        if not os.path.exists(os.path.join(D, "msm", p["thumb"])): continue
        try: ds = f'{date.fromisoformat(p["edition"]):%b} {date.fromisoformat(p["edition"]).day}'
        except Exception: ds = ""
        old = p.get("edition") != ed["date"]
        lab = f'<span class="old">{e(ds)} edition (latest posted)</span>' if old else f'{e(ds)} print edition'
        figs.append(f'<figure class="fp-i"><button type="button" data-full="{e(p["file"])}" data-name="{e(p["name"])}" data-site="{e(p["site"])}" aria-label="Enlarge the front page of {e(p["name"])}">'
                    f'<img src="{e(p["thumb"])}" alt="Front page of {e(p["name"])}, {e(ds)}" loading="lazy"></button>'
                    f'<figcaption><b>{e(p["name"])}</b>{lab}</figcaption></figure>')
    if not figs: return ""
    js = ("<script>(function(){var b=document.getElementById('fp-box'),im=b.querySelector('img'),t=b.querySelector('span'),l=b.querySelector('a');"
          "function c(){b.className='';im.removeAttribute('src');document.body.style.overflow=''}"
          "document.querySelectorAll('.fp-i button').forEach(function(x){x.addEventListener('click',function(){im.src=x.dataset.full;im.alt=x.dataset.name;t.textContent=x.dataset.name+' · ';l.href=x.dataset.site;b.className='on';b.scrollTop=0;document.body.style.overflow='hidden'})});"
          "b.addEventListener('click',function(ev){if(ev.target.tagName!=='A')c()});document.addEventListener('keydown',function(ev){if(ev.key==='Escape')c()})})()</script>")
    return ('<section class="fp" aria-label="Front pages"><div class="fp-row">' + "".join(figs) + "</div>"
            f'<p class="fp-credit">{e(fp.get("credit","Front pages via Freedom Forum"))}. Tap a page to enlarge it.</p></section>'
            '<div id="fp-box" role="dialog" aria-modal="true" aria-label="Front page"><img alt=""><p><span></span><a href="#" target="_blank" rel="noopener">Open the outlet’s site</a> · Tap anywhere or press Esc to close</p></div>' + js)

def edition_html(ed, front=False):
    out = []
    if front: out.append(frontpages_html(ed))
    if ed.get("intro"): out.append(f'<p class="summary" style="font-size:18px;margin:14px 0 0"><i>{e(ed["intro"])}</i></p>')
    out.append('<section class="msm-sec"><h2>What’s leading</h2><p class="note">The stories the big newsrooms put at the top. Stories shared by several outlets come first.</p>'
               + "".join(item(i) for i in ed.get("leading", [])) + "</section>")
    mr = "".join(f'<div><h4>{e(o["outlet"])}</h4><p class="lst">{e(o.get("list",""))}</p><ol>' + "".join(f'<li>{a(x["url"], x["headline"])}</li>' for x in o["items"]) + "</ol></div>" for o in ed.get("most_read", []))
    out.append(f'<section class="msm-sec"><h2>Most read</h2><div class="mr-grid">{mr}</div></section>')
    ob = "".join(f'<div class="ob"><h4>{a(o["home"], o["name"])}</h4><p>{e(o.get("para",""))}</p><ol>' + "".join(f'<li>{a(x["url"], x["headline"])}</li>' for x in o["items"]) + "</ol></div>" for o in ed.get("outlets", []))
    out.append(f'<section class="msm-sec"><h2>Outlet by outlet</h2><div class="msm-cols">{ob}</div></section>')
    isr = ed.get("israel", {})
    if isr:
        out.append(f'<section class="msm-sec"><h2>Israel in the mainstream</h2><p class="note" style="font-style:normal;font-size:15px;color:#222">{e(isr.get("para",""))}</p>'
                   + "".join(item(i, False) for i in isr.get("items", [])) + "</section>")
    out.append('<section class="msm-sec"><h2>Culture &amp; life</h2><div class="msm-cols">' + "".join(item(i, False) for i in ed.get("culture", [])) + "</div></section>")
    out.append('<section class="msm-sec"><h2>Sports</h2>' + "".join(item(i, False) for i in ed.get("sports", [])) + "</section>")
    foot = f'<div class="msm-foot"><p><b>How this was read.</b> {e(ed.get("method",""))}</p>'
    if ed.get("unread"):
        foot += "<p><b>Could not read:</b></p><ul>" + "".join(f'<li>{e(u["outlet"])}: {e(u["tried"])}</li>' for u in ed["unread"]) + "</ul>"
    return "".join(out) + foot + "</div>"

def page(ed, eds, root, now, here_date):
    arch = [x for x in eds if x["date"] != here_date]
    links = "".join(f'<li><a href="{root}msm/archive/{x["date"]}.html">{e(long_date(x["date"]))}</a></li>' for x in arch[:60])
    back = "" if here_date == eds[0]["date"] else f'<p class="srcs"><a href="{root}msm/">← Today’s edition</a></p>'
    arch_html = f'<section class="msm-sec"><h2>Earlier editions</h2><ul>{links}</ul></section>' if arch else '<section class="msm-sec"><h2>Earlier editions</h2><p class="empty">This is the first edition.</p></section>'
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>MSM — {e(long_date(ed["date"]))}</title>'
            f'<style>{CSS}{EXTRA}</style></head><body><div class="page">{sitenav.nav("msm", root)}'
            '<header class="masthead"><h1>MSM</h1><p class="sub">What the big newsrooms are leading with, and what their readers are reading</p>'
            f'<div class="dateline"><span>{e(long_date(ed["date"]))}</span><span>NYT · Washington Post · BBC · Guardian · The Times · Times of Israel · ynet</span></div></header>'
            + back + edition_html(ed, here_date == eds[0]["date"]) + arch_html +
            f'<p class="srcs">Page built {now:%d %B %Y, %H:%M} Israel time.</p></div></body></html>')

def fetch_frontpages():
    """Refresh msm/frontpages/ first. Never blocks or breaks the build."""
    try:
        import subprocess, sys
        subprocess.run([sys.executable, os.path.join(D, "msm/fetch_frontpages.py")], timeout=240, check=False)
    except Exception as ex:
        print("front page fetch skipped:", ex)

def main():
    fetch_frontpages()
    d = json.load(open(os.path.join(D, "msm/data.json"), encoding="utf-8"))
    eds = sorted(d["editions"], key=lambda x: x["date"], reverse=True)
    now = datetime.now(TZ)
    os.makedirs(os.path.join(D, "msm/archive"), exist_ok=True)
    open(os.path.join(D, "msm/index.html"), "w", encoding="utf-8").write(page(eds[0], eds, "../", now, eds[0]["date"]))
    for x in eds[1:]:
        open(os.path.join(D, f"msm/archive/{x['date']}.html"), "w", encoding="utf-8").write(page(x, eds, "../../", now, x["date"]))
    print(f"wrote msm/index.html ({eds[0]['date']}) and {len(eds)-1} archive page(s)")

if __name__ == "__main__":
    main()
