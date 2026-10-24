#!/usr/bin/env python3
"""Build haiti/index.html from haiti/data.json. Usage: python3 build_haiti.py  (data in haiti/data.json; see haiti/README.md)"""
import os, json
from datetime import datetime
from build import CSS, TZ, e
from build_yemen import NAV_CSS
D = os.path.dirname(os.path.abspath(__file__))
EXTRA = ('.hz{max-width:1100px;margin:0 auto}.hz h1{font-size:34px;margin:14px 0 6px}.hz h2{border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a;padding:5px 0;margin:26px 0 12px;font-family:Helvetica,Arial,sans-serif;font-size:14px;letter-spacing:2px;text-transform:uppercase}'
 '.hz .it{border-top:1px solid #bbb;padding:10px 0}.hz .when{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#7a1f1f;letter-spacing:.5px}.hz .who{font-weight:700}.hz .meta{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555;margin:4px 0}'
 '.hz .oth{font-size:14px;border-left:3px solid #bbb;padding-left:8px;margin:6px 0}.hz table{border-collapse:collapse;width:100%;font-size:14px}.hz th,.hz td{border:1px solid #ccc;padding:6px 8px;text-align:left;vertical-align:top}.hz ul{margin:4px 0 8px 20px;padding:0}.hz li{margin-bottom:5px}')
def a(u, t): return f'<a href="{e(u)}" target="_blank" rel="noopener">{e(t)}</a>'
def build(now):
    d = json.load(open(os.path.join(D, "haiti/data.json"), encoding="utf-8"))
    S = d["sections"]; h = []
    h.append(f'<h1>{e(d["title"])}</h1><p class="meta">Updated {e(d["updated"])} Israel time. Each item says who said it, where, when, and what comes with it. Nothing here is graded. Where sources differ, the item says "another source says" and the judgment is yours.</p>')
    h.append('<h2>Latest, newest first</h2>')
    for x in d["feed"]:
        h.append(f'<div class="it"><div class="when">{e(x["when"])}</div><div><span class="who">{e(x["who"])}</span> · {e(x["where"])}</div><p>{e(x["text"])}</p>'
                 f'<div class="meta">Evidence: {e(x["evidence"])} · {a(x["url"], "open the original")}</div>'
                 + (f'<div class="oth"><b>Another source says:</b> {e(x["other"])}' + "".join(" · " + a(u, t) for t, u in x.get("links", [])) + '</div>' if x.get("other") else '') + '</div>')
    def sec(title, key):
        h.append(f'<h2>{e(title)}</h2><ul>' + "".join(f'<li>{e(t)}</li>' for t in S[key]) + '</ul>')
    sec("El Salvador's operation", "salvador"); sec("The Gang Suppression Force (UN-authorized)", "gsf")
    sec("Haitian police and army", "haitian"); sec("United States", "us"); sec("Special forces and private contractors hired by Haiti's government", "contractors")
    h.append('<h2>The gangs: who they are, where they operate</h2>' + "".join(f'<div class="it"><span class="who">{e(n)}</span><p>{e(t)} {a(u, "source")}</p></div>' for n, t, u in d["gangs"]))
    h.append('<h2>Numbers, as each source gives them</h2><table><tr><th>Measure</th><th>Figures reported</th></tr>' + "".join(f'<tr><td>{e(a_)}</td><td>{e(b)}</td></tr>' for a_, b in d["numbers"]) + '</table>')
    rail = '<aside class="rail"><div class="sources" id="links"><h2>Links</h2>' + "".join(f'<h4>{e(t)}</h4><ul>' + "".join(f'<li>{a(u, n)}</li>' for n, u in ls) + '</ul>' for t, ls in d["links"]) + '</div></aside>'
    nav = __import__("sitenav").nav("haiti", "../")
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(d["title"])}</title><style>{CSS}{NAV_CSS}{EXTRA}</style></head><body><div class="page">{nav}'
            f'<div class="topline"><span>{e(d["title"])}</span><span>Page built {now:%d %B %Y, %H:%M} Israel time</span></div><main class="hz"><div class="layout"><main class="main">{"".join(h)}</main>{rail}</div></main>'
            '<footer>Updated on request and a few times a day while the story moves</footer></div></body></html>')
if __name__ == "__main__":
    open(os.path.join(D, "haiti/index.html"), "w", encoding="utf-8").write(build(datetime.now(TZ))); print("wrote haiti/index.html")
