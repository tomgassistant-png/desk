#!/usr/bin/env python3
"""Build mars/index.html from mars/data.json. Usage: python3 build_mars.py  (data in mars/data.json; see mars/README.md)"""
import os, json, math
from datetime import datetime
from build import CSS, TZ, e
from build_yemen import NAV_CSS
D = os.path.dirname(os.path.abspath(__file__))
EXTRA = ('.mz{max-width:1100px;margin:0 auto}.mz h1{font-size:34px;margin:14px 0 6px}.mz h2{border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a;padding:5px 0;margin:26px 0 12px;font-family:Helvetica,Arial,sans-serif;font-size:14px;letter-spacing:2px;text-transform:uppercase}'
 '.mz h3{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:1px;text-transform:uppercase;color:#444;margin:16px 0 6px}'
 '.mz .it{border-top:1px solid #bbb;padding:10px 0}.mz .when{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#7a1f1f;letter-spacing:.5px}.mz .who{font-weight:700}.mz .meta{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555;margin:4px 0}'
 '.mz .oth{font-size:14px;border-left:3px solid #bbb;padding-left:8px;margin:6px 0}.mz table{border-collapse:collapse;width:100%;font-size:14px}.mz th,.mz td{border:1px solid #ccc;padding:6px 8px;text-align:left;vertical-align:top}.mz ul{margin:4px 0 8px 20px;padding:0}.mz li{margin-bottom:6px}'
 '.mz .course{border:2px solid #1a1a1a;padding:10px 14px;margin:12px 0;font-family:Helvetica,Arial,sans-serif;font-size:15px;background:#f6f3ea}.mz .course a{font-weight:700}'
 '.mz .chip{display:inline-block;font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:700;color:#7a1f1f;border:1px solid #7a1f1f;padding:0 4px;margin-left:4px;letter-spacing:.3px}'
 '.mz .kind{font-family:Helvetica,Arial,sans-serif;font-size:11px;color:#444;border:1px solid #999;padding:0 4px;margin-left:4px}'
 '.mz .counter{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0}.mz .counter div.n{border:1px solid #1a1a1a;padding:8px 12px;min-width:150px}.mz .counter b{display:block;font-family:Helvetica,Arial,sans-serif;font-size:26px}.mz .counter span{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555}'
 '.mz svg{max-width:100%;height:auto;border:1px solid #bbb;background:#faf7f0}'
 '.mz figure{margin:8px 0 10px;max-width:100%}.mz figure img{display:block;max-width:100%;height:auto;max-height:340px;border:1px solid #bbb}.mz figcaption{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555;margin-top:3px;overflow-wrap:anywhere}.mz .srcs{font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#555;margin:6px 0}')
def a(u, t): return f'<a href="{e(u)}" target="_blank" rel="noopener">{e(t)}</a>'
def lk(links): return "".join(" · " + a(u, t) for t, u in links)
def fig(x):
    """Optional picture on a feed item, board row or section: x has image (file under mars/img/), image_alt, image_caption, image_credit (who and license), image_url (source page); and/or photo_link {url,label} for a copyrighted photo we do not copy."""
    out = ""
    if x.get("image"):
        cr = e(x.get("image_credit", ""))
        if x.get("image_url"): cr = a(x["image_url"], x.get("image_credit", ""))
        cap = (e(x["image_caption"]) + " · " if x.get("image_caption") else "") + "Credit: " + cr
        out += f'<figure><img src="{e(x["image"])}" alt="{e(x.get("image_alt") or x.get("image_caption", ""))}" loading="lazy"><figcaption>{cap}</figcaption></figure>'
    pl = x.get("photo_link")
    if pl: out += f'<p class="srcs">Photo (copyrighted, not copied): {a(pl["url"], pl["label"])}</p>'
    return out
def chip(label): return f' <span class="chip">[{e(label)}]</span>' if label else ""
def svg_map(p):
    pts = p["route"]; la0 = sum(x[1] for x in pts) / len(pts); k = math.cos(math.radians(la0))
    xs = [x[0] * k for x in pts]; ys = [x[1] for x in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); W = 640; pad = 24
    sc = (W - 2 * pad) / max(x1 - x0, 1e-9); H = int((y1 - y0) * sc + 2 * pad)
    P = lambda i: (pad + (xs[i] - x0) * sc, pad + (y1 - ys[i]) * sc)
    path = " ".join(f"{P(i)[0]:.1f},{P(i)[1]:.1f}" for i in range(len(pts)))
    sx, sy = P(0); ex, ey = P(len(pts) - 1)
    km_deg = 59.27  # kilometers per degree of latitude on Mars (circumference about 21,344 km)
    bar = km_deg and (2 / km_deg) * sc
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Perseverance route, {len(pts)} waypoints from sol {pts[0][2]} to sol {pts[-1][2]}">'
            f'<polyline points="{path}" fill="none" stroke="#7a1f1f" stroke-width="1.4"/>'
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4" fill="#1a1a1a"/><text x="{sx+7:.1f}" y="{sy-6:.1f}" font-size="11" font-family="Helvetica,Arial">first waypoint in file (sol {pts[0][2]})</text>'
            f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="#c62828"/><text x="{ex-6:.1f}" y="{ey-9:.1f}" font-size="11" text-anchor="end" font-family="Helvetica,Arial">latest waypoint in file (sol {pts[-1][2]})</text>'
            f'<line x1="{pad}" y1="{H-10}" x2="{pad+bar:.1f}" y2="{H-10}" stroke="#1a1a1a" stroke-width="2"/><text x="{pad+bar+6:.1f}" y="{H-6}" font-size="11" font-family="Helvetica,Arial">2 km</text>'
            f'<text x="{W-pad}" y="14" font-size="11" text-anchor="end" font-family="Helvetica,Arial">north is up</text></svg>')
def build(now):
    d = json.load(open(os.path.join(D, "mars/data.json"), encoding="utf-8"))
    P = d["perseverance"]; h = []
    h.append(f'<h1>{e(d["title"])}</h1><p class="meta">Updated {e(d["updated"])} Israel time. Facts checked {e(d["checked"])}. Each item says who said it, when, what, and links to the page. Plans and company claims marked [aspirational] are goals, not funded schedules. [unconfirmed] means I could not match it to a second source.</p>')
    h.append(f'<div class="course"><b>Background:</b> <a href="{e(d["course_url"])}">Background: Scholar\'s Mars course</a> &mdash; how Mars has been explored, a map set, and where each mission stands.</div>')
    h.append('<h2>Summary</h2>' + ''.join(f'<p>{e(t)}</p>' for t in d["narrative"]))
    h.append('<h2>Today and recent, newest first</h2>')
    for x in d["feed"]:
        h.append(f'<div class="it"><div class="when">{e(x["when"])}</div><div><span class="who">{e(x["who"])}</span> · {e(x["where"])} <span class="kind">{e(x["kind"])}</span></div><p>{e(x["text"])}</p>{fig(x)}'
                 f'<div class="meta">Evidence: {e(x["evidence"])} · {a(x["url"], x["link_text"])}</div>'
                 + (f'<div class="oth"><b>Also:</b> {e(x["other"])}' + lk(x.get("links", [])) + '</div>' if x.get("other") else '') + '</div>')
    h.append('<h2>Mission status board</h2><p class="meta">Last checked ' + e(d["checked"]) + '. The date in the last column is the newest source date for that row.</p>')
    for g, rows in d["board"]:
        h.append(f'<h3>{e(g)}</h3><table><tr><th>Mission</th><th>Status</th><th>Source date</th><th>Links</th></tr>' + "".join(
            f'<tr><td><b>{e(r["m"])}</b></td><td>{e(r["s"])}</td><td>{e(r["d"])}</td><td>{" · ".join(a(u, t) for t, u in r["links"]) or "per Scholar\'s course"}</td></tr>' + (f'<tr><td colspan="4">{fig(r)}</td></tr>' if fig(r) else '') for r in rows) + '</table>')
    h.append('<h2>Perseverance counter</h2><div class="counter">'
             f'<div class="n"><b>{P["sol"]}</b><span>last waypoint in NASA\'s file: sol {P["sol"]} ({e(P["sol_date"])})</span></div>'
             f'<div class="n"><b>{P["km"]:.2f} km</b><span>{P["mi"]} miles driven in total (NASA\'s record: 45.22 km on sol 2006)</span></div>'
             f'<div class="n"><b>{P["lat"]:.4f}, {P["lon"]:.4f}</b><span>latitude, longitude (degrees north, east)</span></div></div>'
             + fig(P) + f'<p><b>Area:</b> {e(P["area"])}</p><p><b>Today\'s sol:</b> {e(P["est_sol"])} ({e(P["est_note"])})</p><p class="meta">{e(P["note"])}</p>'
             + svg_map(P) + '<p class="meta">Route drawn from the {n} waypoints in NASA\'s public traverse file, copied 27 Oct 2026. The path loops, so the area covered is far smaller than the distance driven. {l}</p>'.format(n=len(P["route"]), l=" · ".join(a(u, t) for t, u in P["links"])))
    h.append('<h2>Curiosity</h2>' + fig(d.get("curiosity_image", {})) + '<ul>' + "".join(f'<li>{e(x["t"])}{lk(x["links"])}</li>' for x in d["curiosity"]) + '</ul>')
    h.append('<h2>Plans and company claims</h2><p class="meta">Goals unless a budget and a contract exist. Each is labeled.</p><ul>' + "".join(f'<li><b>{e(x["who"])}</b>{chip(x["label"])}: {e(x["t"])}{lk(x["links"])}</li>' for x in d["plans"]) + '</ul>')
    h.append('<h2>Upcoming dates</h2><table><tr><th>When</th><th>What</th></tr>' + "".join(f'<tr><td>{e(w)}</td><td>{e(t)}{chip(l)}</td></tr>' for w, t, l in d["upcoming"]) + '</table>')
    h.append('<h2>Terms</h2><ul>' + "".join(f'<li><b>{e(t)}</b>: {e(x)}</li>' for t, x in d["glossary"]) + '</ul>')
    h.append('<h2>Not read or only partly read</h2><ul>' + "".join(f'<li>{e(t)}</li>' for t in d["not_read"]) + '</ul>')
    rail = '<aside class="rail"><div class="sources" id="links"><h2>Links</h2>' + "".join(f'<h4>{e(t)}</h4><ul>' + "".join(f'<li>{a(u, n)}</li>' for n, u in ls) + '</ul>' for t, ls in d["links"]) + '</div></aside>'
    nav = __import__("sitenav").nav("mars", "../")
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(d["title"])}</title><style>{CSS}{NAV_CSS}{EXTRA}</style></head><body><div class="page">{nav}'
            f'<div class="topline"><span>{e(d["title"])}</span><span>Page built {now:%d %B %Y, %H:%M} Israel time</span></div><main class="mz"><div class="layout"><main class="main">{"".join(h)}</main>{rail}</div></main>'
            '<footer>Updated each morning from primary sources; see mars/README.md for the daily checks</footer></div></body></html>')
if __name__ == "__main__":
    open(os.path.join(D, "mars/index.html"), "w", encoding="utf-8").write(build(datetime.now(TZ))); print("wrote mars/index.html")
