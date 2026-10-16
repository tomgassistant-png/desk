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

def photo(it, root):
    if not it.get("image") and not it.get("photo_link"):
        return ""
    if it.get("image"):
        cr = e(it.get("image_credit", ""))
        if it.get("image_url"):
            cr = f'<a href="{e(it["image_url"])}" target="_blank" rel="noopener">{cr}</a>'
        cap = (e(it["image_caption"]) + " · " if it.get("image_caption") else "") + "Photo: " + cr
        return (f'<figure style="margin:8px 0 10px"><img src="{root}{e(it["image"])}" alt="{e(it.get("image_caption") or it["headline"])}" loading="lazy" '
                f'style="max-width:100%;height:auto;max-height:340px;display:block"><figcaption class="srcs">{cap}</figcaption></figure>')
    pl = it["photo_link"]
    return f'<p class="srcs">Photo (copyrighted, not copied): <a href="{e(pl["url"])}" target="_blank" rel="noopener">{e(pl["label"])}</a></p>'

def story(it, newest, h="h3", root="../../"):
    if isinstance(newest, dict): newest = newest.get(it["section"], "")
    new = it["edition"] == newest
    tag = '<span class="tag-new">New</span>' if new else ""
    url = it["sources"][0]["url"] if it.get("sources") else "#"
    srcs = " · ".join(f'<a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s["name"])}</a>' for s in it.get("sources", []))
    return (f'<article class="story{" new" if new else ""}" id="{e(it["id"])}"><{h}><a href="{e(url)}" rel="noopener" target="_blank">{tag}{e(it["headline"])}</a></{h}>'
            + photo(it, root) + f'<p class="summary">{e(it["text"])}</p><p class="meta srcs">{e(long_date(it["edition"]))} edition · {srcs}</p></article>')

def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(html)

def quote_box(sym="SPCX"):
    import json as _j, urllib.request as _u
    cache = os.path.join(ROOT, "digest/quote_%s.json" % sym)
    q = None
    try:
        r = _u.Request(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1d", headers={"User-Agent": "Mozilla/5.0"})
        m = _j.load(_u.urlopen(r, timeout=20))["chart"]["result"][0]["meta"]
        prev = m.get("previousClose") or m["chartPreviousClose"]
        q = {"price": m["regularMarketPrice"], "prev": prev, "time": m["regularMarketTime"]}
        open(cache, "w").write(_j.dumps(q))
    except Exception:
        try: q = _j.load(open(cache))
        except Exception: q = None
    url = f"https://finance.yahoo.com/quote/{sym}/"
    if not q:
        return f'<div class="quote" style="border:1px solid #ccc;padding:10px;margin:12px 0"><b>SpaceX ({sym}, Nasdaq)</b>: price not available. <a href="{url}" target="_blank" rel="noopener">Yahoo Finance</a></div>'
    ch = q["price"] - q["prev"]; pct = ch / q["prev"] * 100
    col = "#1a7f37" if ch >= 0 else "#b00020"
    t = datetime.fromtimestamp(q["time"], TZ).strftime("%d %b %Y, %H:%M")
    return (f'<div class="quote" style="border:1px solid #ccc;padding:10px 14px;margin:12px 0;display:inline-block">'
            f'<b>SpaceX ({sym}, Nasdaq)</b><br><span style="font-size:1.6em">${q["price"]:,.2f}</span> '
            f'<span style="color:{col}">{ch:+.2f} ({pct:+.2f}%)</span><br>'
            f'<span class="srcs">As of {t} Israel time (last trade). Price from Yahoo Finance, updated at each daily build.</span><br>'
            f'<a href="{url}" target="_blank" rel="noopener">Open SPCX on Yahoo Finance</a></div>')

def polymarket_box(slug, label):
    import json as _j, urllib.request as _u
    cache = os.path.join(ROOT, "digest/polymarket_%s.json" % slug)
    q = None
    try:
        r = _u.Request("https://gamma-api.polymarket.com/events?slug=" + slug, headers={"User-Agent": "Mozilla/5.0"})
        ev = _j.load(_u.urlopen(r, timeout=20))[0]
        rows = []
        for m in ev["markets"]:
            if m.get("closed"): continue
            try: pr = float(_j.loads(m.get("outcomePrices") or "[0]")[0])
            except Exception: continue
            rows.append([m.get("groupItemTitle") or m.get("question"), pr])
        rows.sort(key=lambda x: -x[1])
        q = {"rows": rows[:8], "time": int(datetime.now(TZ).timestamp()), "volume": ev.get("volume")}
        open(cache, "w").write(_j.dumps(q))
    except Exception:
        try: q = _j.load(open(cache))
        except Exception: q = None
    url = "https://polymarket.com/event/" + slug
    if not q:
        return f'<div class="quote" style="border:1px solid #ccc;padding:10px;margin:12px 0"><b>Polymarket: {e(label)}</b>: odds not available. <a href="{url}" target="_blank" rel="noopener">Polymarket</a></div>'
    t = datetime.fromtimestamp(q["time"], TZ).strftime("%d %b %Y, %H:%M")
    li = "".join(f'<tr><td style="padding:1px 10px 1px 0">{e(n)}</td><td style="text-align:right"><b>{p*100:.1f}%</b></td></tr>' for n, p in q["rows"])
    return (f'<div class="quote" style="border:1px solid #ccc;padding:10px 14px;margin:12px 0;display:inline-block">'
            f'<b>Polymarket: {e(label)}</b><table style="font-family:Helvetica,Arial,sans-serif;font-size:14px;margin:6px 0">{li}</table>'
            f'<span class="srcs">Fetched {t} Israel time. Market price of a "Yes" share, updated at each daily build. Odds are bets, not polls.</span><br>'
            f'<a href="{url}" target="_blank" rel="noopener">Open the market on Polymarket</a></div>')

def main():
    d = load("digest/items.json")
    items = d["items"]
    ids = {s["id"] for s in d["sections"]}
    bad = [i["id"] for i in items if i["section"] not in ids or not all(i.get(k) for k in ("id", "edition", "headline", "text"))]
    if bad: raise SystemExit(f"digest/items.json problems: {bad}")
    own = {s["id"] for s in d["sections"] if s.get("own_edition")}
    newest = max(i["edition"] for i in items if i["section"] not in own)
    secnew = {s["id"]: max((i["edition"] for i in items if i["section"] == s["id"]), default="") if s["id"] in own else newest for s in d["sections"]}
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
        todays = [i for i in items if i["section"] == s["id"] and i["edition"] == secnew[s["id"]]]
        if s["id"] in own and todays:
            lines.append(f'<li><b>{e(s["name"])}</b> <a href="../digest/{s["id"]}/#{e(todays[0]["id"])}">{e(todays[0]["headline"])}</a> <span class="srcs">({e(long_date(secnew[s["id"]]))})</span></li>')
        elif todays:
            lines.append(f'<li><b>{e(s["name"])}</b> <a href="../digest/{s["id"]}/#{e(todays[0]["id"])}">{e(todays[0]["headline"])}</a></li>')
        else:
            lines.append(f'<li class="quiet"><b>{e(s["name"])}</b> <a href="../digest/{s["id"]}/">Nothing new today</a></li>')

    # cover: top story of each section in today's edition
    seen, top = set(), []
    for i in items:
        if i["edition"] == newest and i["section"] not in seen:
            seen.add(i["section"]); top.append(i)
    body = "".join(f'<p class="sec">{e(names[i["section"]])}</p>' + story(i, newest, "h2", "../") for i in top)
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
        sn = secnew[s["id"]]
        mine = sorted((i for i in items if i["section"] == s["id"]), key=lambda i: i["edition"], reverse=True)
        out = [head(s["name"] + " — Digest section"), sitenav.nav(s["id"], "../../"),
               f'<header class="masthead"><h1>{e(s["name"])}</h1><p class="dateline">Daily research digest section · latest edition {e(long_date(sn))}</p></header>']
        if s.get("header_image"):
            hi = s["header_image"]
            out.append(f'<figure style="margin:0 0 12px"><img src="../../{e(hi["image"])}" alt="{e(hi.get("caption",""))}" style="width:100%;max-height:320px;object-fit:cover;display:block">'
                       f'<figcaption class="srcs">{e(hi.get("caption",""))} · Photo: <a href="{e(hi["image_url"])}" target="_blank" rel="noopener">{e(hi["image_credit"])}</a></figcaption></figure>')
        sidebar = s.get("baseline_placement") == "sidebar"
        if s.get("baseline") and sidebar:
            paras = s["baseline"] if isinstance(s["baseline"], list) else [s["baseline"]]
            bsrcs = "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a></li>' for l in s.get("baseline_sources", []))
            bg = [head(s["name"] + " — Backgrounder"), sitenav.nav(s["id"], "../../../"),
                  f'<header class="masthead"><h1>{e(s["name"])}: Backgrounder</h1><p class="dateline">'
                  + (f'Last updated: {e(s["baseline_updated"])}' if s.get("baseline_updated") else "") + '</p></header>',
                  f'<p class="srcs"><a href="../">&larr; Back to the {e(s["name"])} section</a></p>']
            bg += [f'<p class="summary">{e(x)}</p>' for x in paras]
            if bsrcs: bg.append(f'<h2 class="edn">Sources</h2><ul class="srcs">{bsrcs}</ul>')
            bg.append('</div></body></html>')
            write(os.path.join(ROOT, f'digest/{s["id"]}/backgrounder/index.html'), "".join(bg))
            teaser = s.get("baseline_teaser") or (paras[0][:180].rsplit(" ", 1)[0] + "…")
            bgbox = ('<aside style="border:1px solid #ccc;border-left:4px solid #8b0000;background:#f1efe8;padding:10px 14px;margin:12px 0">'
                     f'<b>Backgrounder</b><p class="summary" style="margin:6px 0">{e(teaser)}</p>'
                     '<a href="backgrounder/">Read the full backgrounder</a>'
                     + (f'<p class="srcs" style="margin:4px 0"><i>Last updated: {e(s["baseline_updated"])}</i></p>' if s.get("baseline_updated") else "") + '</aside>')
        if s.get("baseline") and not sidebar:
            paras = s["baseline"] if isinstance(s["baseline"], list) else [s["baseline"]]
            srcs = " · ".join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in s.get("baseline_sources", []))
            out.append('<div class="baseline" style="background:#f1efe8;border-left:4px solid #8b0000;padding:12px 16px;margin:12px 0">'
                       '<b>Background</b>' + "".join('<p style="margin:6px 0">' + e(x) + '</p>' for x in paras)
                       + (f'<p class="srcs" style="margin:4px 0">Sources: {srcs}</p>' if srcs else "")
                       + (f'<p class="srcs" style="margin:4px 0"><i>Last updated: {e(s["baseline_updated"])}</i></p>' if s.get("baseline_updated") else "")
                       + '</div>')
        if s.get("links"):
            out.append('<p class="summary">' + " · ".join(f'<a href="{e(l["url"])}">{e(l["label"])}</a>' for l in s["links"]) + '</p>')
        if s.get("about"):
            out.append(f'<p class="summary"><i>{e(s["about"])}</i></p>')
        side = ""
        if s.get("useful_links"):
            side = ('<aside style="border:1px solid #ccc;padding:10px 14px;margin:12px 0;min-width:220px"><b>Useful links</b><ul style="margin:6px 0;padding-left:18px">'
                    + "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a></li>' for l in s["useful_links"]) + '</ul></aside>')
        if sidebar:
            rail = (bgbox if s.get("baseline") else "") + (polymarket_box(s["polymarket"]["slug"], s["polymarket"]["label"]) if s.get("polymarket") else "") + side
            out.append('<div class="cov-grid"><main>')
        elif s["id"] == "spacex-xai-and-cursor" or side or s.get("polymarket"):
            out.append('<div style="display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start">'
                       + (quote_box("SPCX") if s["id"] == "spacex-xai-and-cursor" else "")
                       + (polymarket_box(s["polymarket"]["slug"], s["polymarket"]["label"]) if s.get("polymarket") else "") + side + '</div>')
        if not mine:
            out.append(f'<p class="summary">{e(s.get("placeholder") or "No stories in this section yet. The digest reports on it only when there is material news.")}</p>')
        last = None
        for i in mine:
            if i["edition"] != last:
                last = i["edition"]; out.append(f'<h2 class="edn">{e(long_date(last))}{" · today" if last == sn else ""}</h2>')
            out.append(story(i, secnew))
        if sidebar:
            out.append(f'</main><aside class="rail">{rail}</aside></div>')
        out.append('</div></body></html>')
        write(os.path.join(ROOT, f'digest/{s["id"]}/index.html'), "".join(out))
    bgp = os.path.join(ROOT, "digest/trenton/backgrounder.json")
    if os.path.exists(bgp):
        b = json.load(open(bgp, encoding="utf-8"))
        o = [head(b["title"]), sitenav.nav("trenton", "../../../"),
             f'<header class="masthead"><h1>{e(b["title"])}</h1><p class="dateline">Trenton backgrounder · {e(b["date"])} · <a href="../">Back to the Trenton section</a></p></header>']
        if b.get("image"):
            o.append(f'<figure style="margin:0 0 12px"><img src="../../../{e(b["image"])}" alt="{e(b["image_caption"])}" style="width:100%;max-height:340px;object-fit:cover;display:block">'
                     f'<figcaption class="srcs">{e(b["image_caption"])} · Photo: <a href="{e(b["image_url"])}" target="_blank" rel="noopener">{e(b["image_credit"])}</a></figcaption></figure>')
        o.append(f'<p class="summary"><b>{e(b["summary"])}</b></p>')
        for part in b["parts"]:
            o.append(f'<h2 class="edn">{e(part["h"])}</h2>' + "".join(f'<p class="summary">{e(x)}</p>' for x in part["p"]))
            if part.get("note"): o.append(f'<p class="srcs"><i>{e(part["note"])}</i></p>')
            o.append('<p class="srcs">Sources: ' + " · ".join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in part["sources"]) + '</p>')
        o.append('</div></body></html>')
        write(os.path.join(ROOT, "digest/trenton/backgrounder/index.html"), "".join(o))
    print(f"cover + {len(d['sections'])} sections built; edition {newest}, {len(items)} items")

if __name__ == "__main__":
    main()
