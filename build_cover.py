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
            + photo(it, root) + f'<p class="summary">{e(it["text"])}</p>' + ("".join(f'<p class="summary">{e(x)}</p>' for x in it.get("body", [])) if h != "h2" else "")
            + (('<details class="more"><summary><b>More: the rest of the session</b></summary>' + "".join(f'<p class="summary">{e(x)}</p>' for x in it["more"]) + '</details>') if it.get("more") and h != "h2" else "")
            + f'<p class="meta srcs">{e(long_date(it["edition"]))} edition · {srcs}</p></article>')

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

def render_timestamped(b, secid, slug, names):
    """Backgrounder with a timestamped video summary: every time links to the video at that second."""
    R = "../../../"
    vid = b["video"]
    def ts(t):
        t = int(t); return f"{t//3600}:{t//60%60:02d}:{t%60:02d}"
    def lk(t, label=None):
        return f'<a href="https://www.youtube.com/watch?v={e(vid)}&amp;t={int(t)}s" target="_blank" rel="noopener">{e(label or ts(t))}</a>'
    o = [head(b["title"]), sitenav.nav(secid, R),
         f'<header class="masthead"><h1>{e(b["title"])}</h1><p class="dateline">{e(names.get(secid, secid))} backgrounder · {e(b["date"])} · <a href="../">Back to the section</a></p></header>',
         f'<p class="summary"><b>{e(b["summary"])}</b></p>',
         f'<p class="srcs">Video: <a href="https://www.youtube.com/watch?v={e(vid)}" target="_blank" rel="noopener">Nick Land x Fans on YouTube (CYPHERS)</a> · <a href="transcript/">Full timestamped transcript (auto-captions, with errors)</a> · <a href="transcript.txt">Raw transcript text file</a></p>']
    o.append('<aside style="border:1px solid #ccc;border-left:4px solid #8b0000;background:#f1efe8;padding:10px 14px;margin:12px 0"><b>Method and limits</b>'
             '<p class="summary" style="margin:6px 0">The text comes from YouTube\'s automatic English captions, read by a script. No person has checked it against the audio. '
             'Captions are readable but often wrong on names and terms. Examples: "Ned" for Net, "Sydney" for Patallax, "Luis Electron", "Casey" or "Katie" for Lemur, "Kyodo school" for the Kyoto school, "RA" for rigor, "neog" for numogram, "Ryan Her" for Ryan Haecker. '
             'The captions have no speaker names. A ">>" in the transcript only marks that the speaker changed. This page attributes words to Nick Land only where the context makes it clear that he is answering a question. Other speakers are named only where the chapter title or a host\'s introduction says who is asking; otherwise the page says "speaker unclear".</p>'
             '<p class="summary" style="margin:6px 0">Quoted passages are exact caption text, including caption mistakes, which are noted. Words in square brackets or odd spelling come from the captions, not from this page. Every timestamp links to that second of the video. The summaries are written by this digest from the captions. They are shorter than the talk and leave out details, and where a summary relies on chapter titles alone it says "from chapter titles only". A caption error could change the meaning of a passage, so check a quote against the video before you rely on it.</p></aside>')
    o.append('<h2 class="edn">At a glance</h2><table class="srcs" style="border-collapse:collapse">' + "".join(
        f'<tr><td style="vertical-align:top;padding:3px 12px 3px 0"><b>{e(x["k"])}</b></td><td style="padding:3px 0">{e(x["v"])}</td></tr>' for x in b["facts"]) + '</table>')
    o.append('<h2 class="edn">Land\'s most notable statements</h2><ul>' + "".join(f'<li class="summary">{lk(n["t"])} {e(n["text"])}</li>' for n in b["notable"]) + '</ul>')
    o.append('<h2 class="edn">Chapter index</h2><ol style="padding-left:22px">' + "".join(
        f'<li class="summary"><a href="#c{i}">{e(c["title"])}</a> ({lk(c["start"])} to {ts(c["end"])})</li>' for i, c in enumerate(b["sections"])) + '</ol>')
    for i, c in enumerate(b["sections"]):
        o.append(f'<h2 class="edn" id="c{i}">{lk(c["start"])} {e(c["title"])}</h2>')
        o.append(f'<p class="srcs"><i>{e(c["basis"])}</i></p>')
        o.append("".join(f'<p class="summary">{e(x)}</p>' for x in c["paras"]))
        o.append('<p class="srcs"><b>Timeline</b></p><ul>' + "".join(f'<li class="srcs">{lk(x["t"])} {e(x["text"])}</li>' for x in c["timeline"]) + '</ul>')
        if c["quotes"]:
            o.append('<p class="srcs"><b>Quotes (exact caption text)</b></p>')
            for q in c["quotes"]:
                o.append(f'<blockquote style="margin:8px 0 8px 12px;padding-left:10px;border-left:3px solid #8b0000"><p class="summary" style="margin:0">&ldquo;{e(q["quote"])}&rdquo;</p>'
                         f'<p class="srcs" style="margin:2px 0">{e(q["speaker"])} · {lk(q["t"])}' + (f' · <i>{e(q["note"])}</i>' if q.get("note") else "") + '</p></blockquote>')
    o.append('<p class="srcs"><a href="transcript/">Read the full timestamped transcript</a></p></div></body></html>')
    write(os.path.join(ROOT, f"digest/{secid}/{slug}/index.html"), "".join(o))
    # transcript page, built from the raw text file next to the page
    tp = os.path.join(ROOT, f"digest/{secid}/{slug}/transcript.txt")
    if os.path.exists(tp):
        import re as _re
        t = [head("Nick Land x Fans: auto-caption transcript"), sitenav.nav(secid, R + "../"),
             '<header class="masthead"><h1>Nick Land x Fans: auto-caption transcript</h1><p class="dateline">Cypherboria backgrounder · <a href="../">Back to the summary</a></p></header>',
             '<aside style="border:1px solid #ccc;border-left:4px solid #8b0000;background:#f1efe8;padding:10px 14px;margin:12px 0"><b>Read this first.</b> This is YouTube\'s automatic captioning, with no human correction. Names and terms are often wrong, there are no speaker labels, and ">>" marks only that the speaker changed. '
             'Each timestamp links to that point in the video. Check anything you quote against the audio.</aside>']
        for ln in open(tp, encoding="utf-8").read().split("\n"):
            m = _re.match(r"\[(\d+):(\d+):(\d+)\] (.*)$", ln)
            if not m: continue
            secs_ = int(m[1])*3600 + int(m[2])*60 + int(m[3])
            t.append(f'<p class="summary" style="margin:6px 0"><b>{lk(secs_, "[" + ts(secs_) + "]")}</b> {e(m[4])}</p>')
        t.append('</div></body></html>')
        write(os.path.join(ROOT, f"digest/{secid}/{slug}/transcript/index.html"), "".join(t))


def prayer_box():
    """Today's prayer from the Veil and Light app (digest/cypherboria/prayer/content.js, owned by Tomji; read only).
    Same pick as the app's own 'Today' session: non-night sessions, indexed by days since 1970 on the Israel date."""
    import re, datetime as _dt
    try:
        raw = open(os.path.join(ROOT, "digest/cypherboria/prayer/content.js"), encoding="utf-8").read()
        D = json.loads(raw[raw.index("{"):raw.rindex("}") + 1])
        t = datetime.now(TZ).date()
        di = (t - _dt.date(1970, 1, 1)).days
        pool = [x for x in D["sessions"] if not x.get("night")]
        s = pool[di % len(pool)]
        cat = {c["id"]: c["name"] for c in D["cats"]}.get(s["cat"], "")
    except Exception as ex:
        print("prayer box failed:", ex)
        return ""
    reads = "".join(
        '<details style="margin:4px 0"><summary><b>' + e(p["ref"]) + '</b> <span class="srcs">King James Version</span></summary>'
        + '<p style="margin:6px 0">' + " ".join(f'<sup>{v["n"]}</sup>{e(v["t"])}' for v in p["verses"]) + '</p></details>'
        for p in s["read"])
    return ('<section class="todays-prayer" style="background:#f1efe8;border-left:4px solid #8b0000;padding:12px 18px;margin:12px 0">'
            f'<p class="srcs" style="margin:0 0 2px;text-transform:uppercase;letter-spacing:1px">Today\'s prayer · {e(weekday_date(datetime.combine(t, datetime.min.time())))} · {e(cat)}</p>'
            f'<h2 style="margin:0 0 6px;font-size:22px">{e(s["title"])}</h2>'
            + reads
            + '<div style="margin-top:8px">' + "".join(f'<p style="margin:6px 0;font-size:17px">{e(x)}</p>' for x in s["prayer"]) + '</div>'
            + '<p class="srcs" style="margin:8px 0 0"><a href="prayer/">Open the full session in Veil and Light (scripture, meditation, prayer, closing) →</a></p>'
            '</section>')


def main():
    d = sitenav.load_digest()
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
            prev = sorted((i for i in items if i["section"] == s["id"]), key=lambda i: i["edition"], reverse=True)
            if prev:
                lines.append(f'<li class="quiet"><b>{e(s["name"])}</b> <a href="../digest/{s["id"]}/#{e(prev[0]["id"])}">{e(prev[0]["headline"])}</a> <span class="srcs">(latest, {e(long_date(prev[0]["edition"]))})</span></li>')
            else:
                lines.append(f'<li class="quiet"><b>{e(s["name"])}</b> <a href="../digest/{s["id"]}/">Nothing yet</a></li>')

    # cover: top story of each section in today's edition
    seen, top = set(), []
    for i in items:
        if i["edition"] == newest and i["section"] not in seen:
            seen.add(i["section"]); top.append(i)
    body = "".join(f'<p class="sec">{e(names[i["section"]])}</p>' + story(i, newest, "h2", "../") for i in top)
    # one search index over every section: digest sections, Judea and Samaria, Yemen
    sidx = []
    for i in items:
        srcs = i.get("sources") or []
        sn_ = " ".join(x.get("name", "") for x in srcs if isinstance(x, dict))
        sidx.append({"headline": i["headline"], "summary": (i.get("lead") or i["text"])[:400], "source": sn_, "section_name": names[i["section"]],
                     "edition": i["edition"], "date_long": long_date(i["edition"]), "url": f'../digest/{i["section"]}/#{i["id"]}'})
    for it in load("search-index.json", {}).get("items", []):
        sidx.append({"headline": it["headline"], "summary": it.get("summary", "")[:400], "source": it.get("source", ""), "section_name": "Judea & Samaria · " + it.get("section_name", ""),
                     "edition": it["edition"], "date_long": long_date(it["edition"]), "url": f'../#{it["id"]}'})
    for y_ in load("yemen/items.json", {}).get("editions", []):
        for it in y_.get("items", []):
            sidx.append({"headline": it["headline"], "summary": it.get("text", "")[:400], "source": "", "section_name": "Yemen", "edition": y_["date"],
                         "date_long": long_date(y_["date"]), "url": "../yemen/"})
    write(os.path.join(ROOT, "cover/search-index.json"), json.dumps({"built": now.isoformat(), "count": len(sidx), "items": sidx}, ensure_ascii=False))
    srch = ('<form class="search" id="csearch" role="search" onsubmit="return false" style="margin:10px 0"><input type="search" id="cq" placeholder="Search every section" aria-label="Search every section" autocomplete="off" style="width:70%;max-width:420px;padding:6px 8px;font-size:15px"> '
            '<button type="button" id="cclear">Clear</button></form><section id="cresults" hidden aria-live="polite"></section>'
            """<script>(function(){var q=document.getElementById('cq'),r=document.getElementById('cresults'),idx=null,pend=false;if(!q||!window.fetch)return;
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function load(){if(idx||pend)return;pend=true;fetch('search-index.json',{cache:'no-cache'}).then(function(x){return x.json()}).then(function(d){idx=d.items.map(function(it){it._t=[it.headline,it.summary,it.source,it.section_name,it.edition,it.date_long].join(' ').toLowerCase();return it});run()}).catch(function(){r.hidden=false;r.innerHTML='<p>The search index could not be loaded.</p>'})}
function run(){var v=q.value.trim().toLowerCase();if(!v){r.hidden=true;r.innerHTML='';document.querySelector('.cov-grid').style.display='';return}
document.querySelector('.cov-grid').style.display='none';r.hidden=false;if(!idx){r.innerHTML='<p>Searching…</p>';load();return}
var w=v.split(/\\s+/),m=idx.filter(function(it){return w.every(function(x){return it._t.indexOf(x)>=0})});
var h='<h2 class="edn">'+m.length+' result'+(m.length==1?'':'s')+' for “'+esc(q.value.trim())+'”</h2>';
m.slice(0,200).forEach(function(it){h+='<article class="story"><p class="sec">'+esc(it.section_name)+' · '+esc(it.date_long)+'</p><h3><a href="'+esc(it.url)+'">'+esc(it.headline)+'</a></h3><p class="summary">'+esc(it.summary)+'</p></article>'});r.innerHTML=h}
q.addEventListener('focus',load);q.addEventListener('input',run);document.getElementById('cclear').addEventListener('click',function(){q.value='';run();q.focus()});
q.addEventListener('keydown',function(ev){if(ev.key==='Escape'){q.value='';run()}});})();</script>""")
    cover = (head("Tom's Cover — " + long_date(newest)) + sitenav.nav("cover", "../") +
             f'<header class="masthead"><h1>Tom\'s Cover</h1><p class="dateline">{e(weekday_date(now.date()))} · Digest edition of {e(long_date(newest))}</p></header>'
             + srch + (f'<p class="summary"><i>{e(ed["intro"])}</i></p>' if ed.get("intro") else "") +
             f'<div class="cov-grid"><main><h2 class="edn">Top stories</h2>{body}'
             + (f'<p class="srcs">{e(ed["quiet"])}</p>' if ed.get("quiet") else "") +
             f'</main><aside class="rail">{weather_html(d)}<h2 class="edn">Latest by section</h2><ul class="cov-list">{"".join(lines)}</ul></aside></div>'
             f'<p class="srcs">Built {e(now.strftime("%Y-%m-%d %H:%M"))} Israel time from the daily research digest.</p></div><script>{JS}</script></body></html>')
    write(os.path.join(ROOT, "cover/index.html"), cover)

    # section pages with archive by edition
    for s in d["sections"]:
        sn = secnew[s["id"]]
        mine = sorted((i for i in items if i["section"] == s["id"]), key=lambda i: i["edition"], reverse=True)
        out = [head(s["name"] + " — Digest section"), sitenav.nav(s["id"], "../../"),
               f'<header class="masthead"><h1>{e(s["name"])}</h1><p class="dateline">{("Daily research digest section · latest edition " + e(long_date(sn))) if sn else ("Published by the " + e(s["name"]) + " assistant" + ((" · updated " + e(long_date(s["updated"]))) if s.get("updated") else ""))}</p></header>']
        if s.get("header_image"):
            hi = s["header_image"]
            out.append(f'<figure style="margin:0 0 12px"><img src="../../{e(hi["image"])}" alt="{e(hi.get("caption",""))}" style="width:100%;max-height:320px;object-fit:cover;display:block">'
                       f'<figcaption class="srcs">{e(hi.get("caption",""))} · Photo: <a href="{e(hi["image_url"])}" target="_blank" rel="noopener">{e(hi["image_credit"])}</a></figcaption></figure>')
        if s["id"] == "cypherboria": out.append(prayer_box())
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
            blhtml = ('<div class="baseline" style="background:#f1efe8;border-left:4px solid #8b0000;padding:12px 16px;margin:12px 0">'
                       '<b>Background</b>' + "".join('<p style="margin:6px 0">' + e(x) + '</p>' for x in paras)
                       + (f'<p class="srcs" style="margin:4px 0">Sources: {srcs}</p>' if srcs else "")
                       + (f'<p class="srcs" style="margin:4px 0"><i>Last updated: {e(s["baseline_updated"])}</i></p>' if s.get("baseline_updated") else "")
                       + '</div>')
            if s.get("baseline_position") != "bottom": out.append(blhtml); blhtml = ""
        else:
            blhtml = ""
        if s.get("links"):
            out.append('<p class="summary">' + " · ".join(f'<a href="{e(l["url"])}">{e(l["label"])}</a>' for l in s["links"]) + '</p>')
        if s.get("about"):
            out.append(f'<p class="summary"><i>{e(s["about"])}</i></p>')
        side = ""
        if s.get("useful_links"):
            side = ('<aside style="border:1px solid #ccc;padding:10px 14px;margin:12px 0;min-width:220px"><b>Useful links</b><ul style="margin:6px 0;padding-left:18px">'
                    + "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a></li>' for l in s["useful_links"]) + '</ul></aside>')
        if s["id"] == "trenton" and not s.get("rail_boxes"):
            try:
                import realestate; side = side + realestate.box()
            except Exception as ex:
                print("realestate box failed:", ex)
        if s.get("rail_boxes"):
            # Section keeps its baseline in the main column but moves backgrounders, trackers and links to the rail
            bgl = "".join(f'<div style="margin:8px 0"><a href="{e(b["url"])}"><b>{e(b["label"])}</b></a>'
                          + (f'<p class="summary" style="margin:4px 0;font-size:14px">{e(b["teaser"])}</p>' if b.get("teaser") else "")
                          + (f'<p class="srcs" style="margin:2px 0"><i>Last updated: {e(b["updated"])}</i></p>' if b.get("updated") else "") + '</div>'
                          for b in s.get("backgrounders", []))
            rbox = ('<aside style="border:1px solid #ccc;border-left:4px solid #8b0000;background:#f1efe8;padding:10px 14px;margin:12px 0">'
                    f'<b>Backgrounders</b>{bgl}</aside>') if bgl else ""
            re_html = ""
            if s["id"] == "trenton":
                try:
                    import realestate; re_html = realestate.box()
                except Exception as ex:
                    print("realestate box failed:", ex)
            ul = ('<aside style="border:1px solid #ccc;padding:10px 14px;margin:12px 0"><b>Useful links</b><ul style="margin:6px 0;padding-left:18px">'
                  + "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a></li>' for l in s.get("useful_links", [])) + '</ul></aside>') if s.get("useful_links") else ""
            ppl = ""
            if s.get("watch_people"):
                ppl = ('<aside style="border:1px solid #ccc;padding:10px 14px;margin:12px 0"><b>People watched</b>'
                       + "".join(f'<div style="margin:8px 0"><b>{e(pp["name"])}</b>' + (f' <span class="srcs">{e(pp["handle"])}</span>' if pp.get("handle") else "")
                                 + f'<p class="summary" style="margin:3px 0;font-size:14px">{e(pp["who"])}</p>'
                                 + (f'<p class="srcs" style="margin:2px 0"><i>Confidence: {e(pp["confidence"])}</i></p>' if pp.get("confidence") else "")
                                 + '<p class="srcs" style="margin:2px 0">' + " · ".join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in pp.get("links", [])) + '</p></div>'
                                 for pp in s["watch_people"]) + '</aside>')
            lg = "".join('<aside style="border:1px solid #ccc;padding:10px 14px;margin:12px 0">' + f'<b>{e(g["title"])}</b><ul style="margin:6px 0;padding-left:18px">'
                         + "".join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a></li>' for l in g["links"]) + '</ul></aside>'
                         for g in s.get("link_groups", []))
            rail = rbox + re_html + ul + lg + ppl
            side = ""; sidebar = True
            out.append('<div class="cov-grid"><main>')
        elif sidebar:
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
        if blhtml: out.append(blhtml)
        if sidebar:
            out.append(f'</main><aside class="rail">{rail}</aside></div>')
        out.append('</div></body></html>')
        write(os.path.join(ROOT, f'digest/{s["id"]}/index.html'), "".join(out))
        for old_id in s.get("redirect_from", []):
            tgt = f'../{s["id"]}/'; full = f'https://tomgassistant-png.github.io/desk/digest/{s["id"]}/'
            write(os.path.join(ROOT, f'digest/{old_id}/index.html'),
                  f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">'
                  f'<link rel="canonical" href="{full}"><meta http-equiv="refresh" content="0; url={tgt}"><title>Moved to {e(s["name"])}</title>'
                  f'<script>location.replace("{tgt}"+location.hash)</script></head><body><p>This section is now <a href="{tgt}">{e(s["name"])}</a>.</p></body></html>')
    import glob
    jobs = []
    if os.path.exists(os.path.join(ROOT, "digest/trenton/backgrounder.json")):
        jobs.append((os.path.join(ROOT, "digest/trenton/backgrounder.json"), "trenton", "backgrounder"))
    for f in sorted(glob.glob(os.path.join(ROOT, "digest/*/backgrounders/*.json"))):
        jobs.append((f, f.split(os.sep)[-3], os.path.splitext(os.path.basename(f))[0]))
    for bgp, secid, slug in jobs:
        b = json.load(open(bgp, encoding="utf-8"))
        if b.get("kind") == "timestamped":
            render_timestamped(b, secid, slug, names); continue
        R = "../../../"
        fig = lambda im: (f'<figure style="margin:10px 0 12px"><img src="{R}{e(im["image"])}" alt="{e(im["caption"])}" loading="lazy" style="max-width:100%;max-height:380px;height:auto;display:block">'
                          f'<figcaption class="srcs">{e(im["caption"])} · Photo: <a href="{e(im["image_url"])}" target="_blank" rel="noopener">{e(im["image_credit"])}</a></figcaption></figure>')
        o = [head(b["title"]), sitenav.nav(secid, R),
             f'<header class="masthead"><h1>{e(b["title"])}</h1><p class="dateline">{e(names.get(secid, secid))} backgrounder · {e(b["date"])} · <a href="../">Back to the section</a></p></header>']
        if b.get("image"):
            o.append(fig({"image": b["image"], "caption": b["image_caption"], "image_url": b["image_url"], "image_credit": b["image_credit"]}))
        o.append(f'<p class="summary"><b>{e(b["summary"])}</b></p>')
        for part in b["parts"]:
            o.append(f'<h2 class="edn">{e(part["h"])}</h2>' + "".join(f'<p class="summary">{e(x)}</p>' for x in part["p"]))
            for im in part.get("images", []): o.append(fig(im))
            for lk in part.get("links", []): o.append(f'<p class="srcs">{e(lk.get("prefix",""))}<a href="{e(lk["url"])}" target="_blank" rel="noopener">{e(lk["label"])}</a></p>')
            if part.get("note"): o.append(f'<p class="srcs"><i>{e(part["note"])}</i></p>')
            if part.get("sources"):
                o.append('<p class="srcs">Sources: ' + " · ".join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in part["sources"]) + '</p>')
        o.append('</div></body></html>')
        write(os.path.join(ROOT, f"digest/{secid}/{slug}/index.html"), "".join(o))
    print(f"cover + {len(d['sections'])} sections built; edition {newest}, {len(items)} items")

if __name__ == "__main__":
    main()
