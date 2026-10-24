#!/usr/bin/env python3
"""Build horses/index.html from horses/data.json (wild horse rescue and Western conservation tracker). Usage: python3 build_horses.py"""
import os, json
from datetime import datetime
from build import CSS, TZ, e, long_date
from build_yemen import NAV_CSS

D = os.path.dirname(os.path.abspath(__file__))
EXTRA = ('.hz{max-width:1000px;margin:0 auto}.hz h1{font-size:30px;margin:14px 0 4px}.hz h2{border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a;padding:5px 0;margin:28px 0 12px;font-family:Helvetica,Arial,sans-serif;font-size:14px;letter-spacing:2px;text-transform:uppercase}'
         '.hz table{border-collapse:collapse;width:100%;font-size:14px}.hz th,.hz td{border:1px solid #ccc;padding:6px 8px;vertical-align:top;text-align:left}.hz th{background:#f2f2f2;font-family:Helvetica,Arial,sans-serif;font-size:12px;letter-spacing:.8px;text-transform:uppercase}'
         '.hz .org{border-top:1px solid #bbb;padding:12px 0}.hz .org h3{margin:0 0 2px;font-size:19px}.hz .meta{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555;margin-bottom:6px}'
         '.hz .base{background:#7a1f1f;color:#fff;font-size:10px;letter-spacing:1px;text-transform:uppercase;padding:1px 5px;margin-left:6px;font-family:Helvetica,Arial,sans-serif;vertical-align:middle}'
         '.hz .conf{font-size:13px;color:#444;font-style:italic}.hz .kind{font-family:Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:#7a1f1f}'
         '.hz .dev{border-top:1px dotted #9d968a;padding:8px 0}.hz .big{font-size:22px;font-weight:700}.hz .lede{font-size:16px;line-height:1.45}.hz ul{margin:4px 0 8px 20px;padding:0}')
def link(u, t): return f'<a href="{e(u)}" target="_blank" rel="noopener">{e(t)}</a>'
def gm(p): return f'https://www.google.com/maps/search/?api=1&query={p["lat"]},{p["lon"]}'

def build(now):
    d = json.load(open(os.path.join(D, "horses/data.json"), encoding="utf-8"))
    orgs = {o["id"]: o["name"] for o in d["organizations"]}
    h = []
    h.append('<h1>Wild Horse Rescue and Western Conservation Tracker</h1>')
    h.append(f'<p class="lede">Organizations, campaigns and court and agency actions on wild horses and burros and on conservation in the western United States. Data updated {e(long_date(d["updated"]))}. "Far West" is read here as the western states. Labels on each development: <b>official</b> (BLM or a court docket), <b>advocacy claim</b> (a group\'s own statement), <b>independent reporting</b>, or <b>unconfirmed</b>. All map points are approximate.</p>')
    h.append('<h2>Key numbers</h2><table><tr><th>Measure</th><th>Value</th><th>As of</th><th>Source and note</th></tr>')
    for k in d["key_numbers"]:
        h.append(f'<tr><td>{e(k["label"])}</td><td class="big">{e(k["value"])}</td><td>{e(k["as_of"])}</td><td>{link(k["source_url"], k["source_name"])}. {e(k.get("note",""))}</td></tr>')
    h.append('</table><h2>Developments, newest first</h2>')
    for x in sorted(d["developments"], key=lambda x: x["date"], reverse=True):
        rel = ", ".join(orgs.get(r, r) for r in x.get("related", []))
        h.append(f'<div class="dev"><span class="kind">{e(x["kind"])}</span> · {e(long_date(x["date"]) if len(x["date"])==10 else x["date"])}<br>{e(x["text"])} <span class="meta">Source: {link(x["source_url"], x["source_name"])}{(" · Related: "+e(rel)) if rel else ""}</span></div>')
    h.append('<h2>Organizations</h2><p class="meta">The four baseline organizations come first. Identification problems are stated in each entry.</p>')
    for o in sorted(d["organizations"], key=lambda o: (not o.get("baseline"), o["name"])):
        x = o.get("x")
        xs = (f'{link(x["url"], x["handle"])} ({x["followers"]:,} followers, last post {e(x["last_post_date"])})' if x and x.get("followers") and x.get("last_post_date")
              else (link(x["url"], x["handle"]) if x else 'no official handle found'))
        s = [f'<div class="org"><h3>{e(o["name"])}{"<span class=base>baseline</span>" if o.get("baseline") else ""}</h3>',
             f'<div class="meta">{e(o["type"])} · {e(", ".join(o["states"]))}</div><p>{e(o["summary"])}</p>']
        lt = o.get("latest")
        if lt: s.append(f'<p><b>Latest ({e(lt["date"])}):</b> {e(lt["text"])} {link(lt["url"], "source") if lt.get("url") else ""}</p>')
        elif o.get("latest_note"): s.append(f'<p><b>Latest:</b> {e(o["latest_note"])}</p>')
        if o.get("campaigns"): s.append('<b>Campaigns:</b><ul>' + "".join(f'<li>{e(c)}</li>' for c in o["campaigns"]) + '</ul>')
        s.append(f'<p class="meta">X: {xs}' + (f' · Website: {link(o["website"], o["website"])}' if o.get("website") else '') +
                 (f' · {link(o["nonprofit_check_url"], "ProPublica nonprofit record")}' if o.get("nonprofit_check_url") else '') + '</p>')
        if o.get("financials"): s.append(f'<p class="meta">{e(o["financials"])}</p>')
        if o.get("places"):
            s.append('<p class="meta">Places (approximate): ' + "; ".join(link(gm(p), p["name"]) for p in o["places"]) + '</p>')
        s.append(f'<p class="conf">Confidence: {e(o["confidence"])}</p></div>')
        h.append("".join(s))
    if d.get("x_related"):
        h.append('<h2>Related X accounts</h2><ul>' + "".join(f'<li>{link(r["url"], r["handle"])}: {e(r["relation"])}</li>' for r in d["x_related"]) + '</ul>')
    h.append('<h2>Sources to watch</h2><ul>' + "".join(f'<li>{link(w["url"], w["name"])}: {e(w["how"])}</li>' for w in d["watch_sources"]) + '</ul>')
    h.append('<h2>Notes and limits</h2><ul>' + "".join(f'<li>{e(n)}</li>' for n in d["notes"]) + '</ul>')
    nav = __import__("sitenav").nav("horses", "../")
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>Wild horse rescue and Western conservation tracker</title>'
            f'<style>{CSS}{NAV_CSS}{EXTRA}</style></head><body><div class="page">{nav}'
            f'<div class="topline"><span>Wild Horse Tracker</span><span>Page built {now:%d %B %Y, %H:%M} Israel time</span></div><main class="hz">{"".join(h)}</main>'
            '<footer>Wild Horse Tracker · refreshed on request</footer></div></body></html>')

if __name__ == "__main__":
    open(os.path.join(D, "horses/index.html"), "w", encoding="utf-8").write(build(datetime.now(TZ)))
    print("wrote horses/index.html")
