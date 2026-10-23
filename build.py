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
            + (f'<span class="interim">{e(it["edition_label"])}</span> · ' if it.get("edition_label") else '') +
            f''
            f'<a href="{e(it["url"])}" rel="noopener" target="_blank">{link_text}</a>'
            + (f' · <a href="{e(it["background"])}">Backgrounder</a>' if it.get("background") else '') + '</p>' + places_html(it))

def places_html(it):
    ps = it.get("places") or []
    if not ps:
        return ""
    out = []
    for p in ps:
        la, lo = p["lat"], p["lon"]
        url = f"https://www.openstreetmap.org/?mlat={la}&mlon={lo}#map=15/{la}/{lo}"
        lbl = f'{p["name"]} ({abs(la):.3f}°N, {abs(lo):.3f}°E)'
        note = f' <span class="interim">{e(p["note"])}</span>' if p.get("note") else ""
        out.append(f'<a href="{e(url)}" rel="noopener" target="_blank">{e(lbl)}</a>{note}')
    return '<p class="meta places">Map: ' + " · ".join(out) + '</p>'

NEWEST = None
def is_new(it):
    return NEWEST is not None and it["edition"] == NEWEST
def nc(it):
    return " new" if is_new(it) else ""
def tag(it):
    return '<span class="tag-new">New</span>' if is_new(it) else ""

def article(it, cls="story"):
    return (f'<article class="{cls}{nc(it)}" id="{e(it["id"])}">'
            f'<h3><a href="{e(it["url"])}" rel="noopener" target="_blank">{tag(it)}{e(it["headline"])}</a></h3>'
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
.rail .sources ul{list-style:none;margin:0 0 12px;padding:0}
.rail .sources h4{font-family:Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:#7a1f1f;margin:12px 0 4px}
.rail .sources li{padding:4px 0;font-size:14.5px;line-height:1.3}
.rail .sources li .s{display:inline;margin-left:4px}
.suggest{margin-top:16px;border-top:1px solid #1a1a1a;padding-top:8px;font-size:13px}
.suggest h3{font-family:Helvetica,Arial,sans-serif;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 6px}
.suggest input,.suggest textarea{display:block;width:100%;box-sizing:border-box;font:inherit;font-size:14px;padding:4px 6px;margin:0 0 6px;border:1px solid #1a1a1a;background:#fff;border-radius:0}
.suggest button{font-family:Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:1.2px;text-transform:uppercase;padding:5px 10px;border:1px solid #1a1a1a;background:#1a1a1a;color:#fbf9f4;cursor:pointer}
.suggest .alt{font-size:12px;font-style:italic;color:#555;margin:6px 0 0}
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
.new h2 a,.new h3 a,.new a.h,.new>a{color:#9b1c1c}
.tag-new{display:inline-block;font-family:Helvetica,Arial,sans-serif;font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#fbf9f4;background:#9b1c1c;padding:1px 5px 0;margin-right:7px;vertical-align:2px;line-height:1.5}
.search{max-width:560px;margin:10px auto 0;display:flex;gap:6px}
.search input{flex:1;min-width:0;font:inherit;font-size:16px;padding:6px 9px;border:1px solid #1a1a1a;background:#fff;border-radius:0}
.search button{font-family:Helvetica,Arial,sans-serif;font-size:12px;letter-spacing:1.2px;text-transform:uppercase;padding:0 12px;border:1px solid #1a1a1a;background:#1a1a1a;color:#fbf9f4;cursor:pointer}
.results{margin-top:18px}
.results>h2{font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:2px;text-transform:uppercase;margin:0 0 10px;padding:6px 0 5px;border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a}
.results .story .sec{font-family:Helvetica,Arial,sans-serif;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:#7a1f1f;margin:0 0 3px}
body.searching .layout,body.searching .highlights,body.searching .archive{display:none}
footer{margin-top:28px;border-top:1px solid #1a1a1a;padding-top:8px;font-size:12px;color:#555;text-align:center;font-style:italic}
.wx{margin-bottom:22px;border-top:3px solid #1a1a1a;border-bottom:1px solid #1a1a1a;padding:6px 0 8px;font-family:Helvetica,Arial,sans-serif}
.wx summary{list-style:none;cursor:pointer}
.wx summary::-webkit-details-marker{display:none}
.wx .wl{font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#7a1f1f}
.wx .wn{font-family:Georgia,serif;font-size:30px;font-weight:700;line-height:1.1}
.wx .wn small{font-size:14px;font-weight:400;color:#555;margin-left:4px}
.wx .wd{font-size:13px;color:#333}
.wx .wm{font-size:11px;color:#7a7a7a;margin-top:3px}
.wx table{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px}
.wx th,.wx td{padding:4px 2px;border-bottom:1px dotted #9d968a;text-align:left}
.wx th{font-size:10px;letter-spacing:.8px;text-transform:uppercase;color:#555}
.wx .src{font-size:11px;font-style:italic;color:#555;margin-top:6px}
.wx{padding:6px 8px 8px;transition:background .3s}
.wx.wx-sun{background:#fbf3d6;border-top-color:#c9962a}
.wx.wx-cloud{background:#eceff3;border-top-color:#7d8ca0}
.wx.wx-rain{background:#dfe5ec;border-top-color:#4a6688}
.wx.wx-storm{background:#2f3a48;border-top-color:#e0b43a;border-bottom-color:#2f3a48;color:#f2f2f2}
.wx.wx-storm .wl{color:#f0c96a}.wx.wx-storm .wd,.wx.wx-storm th{color:#e6e6e6}.wx.wx-storm .wn small,.wx.wx-storm .wm,.wx.wx-storm .src{color:#c8ced6}
.wx.wx-storm th,.wx.wx-storm td{border-bottom-color:#5a6778}
.wx .wh{display:flex;align-items:center;gap:8px}.wx .wi{flex:none}
.wx .ws{font-family:Georgia,serif;font-size:15px;font-style:italic}
.wx td .wi{vertical-align:middle;margin-right:4px}
@media (max-width:980px){
 .layout{grid-template-columns:1fr}
 .main{padding-right:0;border-right:none}
 .rail{padding-left:0;margin-top:26px}
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

NAV_CSS = ('.secnav{text-align:center;font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:.5px;'
           'text-transform:uppercase;border-bottom:1px solid #ccc;padding:6px 0;margin-bottom:6px}'
           '.secnav a{color:#222;text-decoration:none;margin:0 10px}.secnav a.on{font-weight:700;border-bottom:2px solid #222}')
NAV = ('<nav class="secnav"><a href="cover/">Cover</a> | <a href="./" class=on>Judea &amp; Samaria</a> | <a href="yemen/">Yemen</a> | '
       '<a href="#backgrounders">Backgrounders</a></nav>')

JS = r"""

(function(){
var b=document.getElementById('wx');if(!b)return;
var L=JSON.parse(b.getAttribute('data-loc'));
var cur=document.getElementById('wxcur'),tb=document.getElementById('wxtab');
var u='https://api.open-meteo.com/v1/forecast?latitude='+L.lat+'&longitude='+L.lon+'&timezone='+encodeURIComponent(L.timezone||'auto')+'&current=temperature_2m,relative_humidity_2m,precipitation,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_max,wind_direction_10m_dominant,sunrise,sunset,daylight_duration&past_days=1&forecast_days=7';
function st(w){if(w==null)return null;if(w<=1)return 'sun';if(w<=3||w==45||w==48)return 'cloud';if(w>=95)return 'storm';if(w>=51&&w<=86)return 'rain';return 'cloud'}
var LB={sun:'Sunny',cloud:'Partly cloudy',rain:'Rain',storm:'Storm'};
function ic(s,z){var C='<path d="M9 19h11a4 4 0 0 0 0-8 6 6 0 0 0-11.5 1.5A3.3 3.3 0 0 0 9 19z" fill="#cfd6df" stroke="#4d5b6b" stroke-width="1.3"/>',S='<circle cx="12" cy="12" r="5" fill="#f2c04a" stroke="#b5841c" stroke-width="1.2"/><g stroke="#b5841c" stroke-width="1.5" stroke-linecap="round"><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/></g>',g;
 if(s=='sun')g=S;else if(s=='cloud')g='<g transform="translate(-2 -3) scale(.8)">'+S+'</g>'+C;
 else if(s=='rain')g='<g transform="translate(0 -3)">'+C+'</g><g stroke="#3d6a9e" stroke-width="1.6" stroke-linecap="round"><path d="M11 19l-1 3M15 19l-1 3M19 19l-1 3"/></g>';
 else g='<g transform="translate(0 -4)">'+C.replace('#cfd6df','#9aa5b3')+'</g><path d="M15 15l-3 5h3l-2 4" fill="none" stroke="#f0b400" stroke-width="1.8" stroke-linejoin="round"/>';
 return '<svg class="wi" width="'+z+'" height="'+z+'" viewBox="0 0 26 26" role="img" aria-label="'+LB[s]+'">'+g+'</svg>'}
function f(c){return Math.round(c*9/5+32)}
function dir(g){return ['N','NE','E','SE','S','SW','W','NW'][Math.round(g/45)%8]}
function fail(){cur.innerHTML='<div class="wd">Weather unavailable</div>';tb.innerHTML=''}
if(!window.fetch){fail();return}
fetch(u).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(d){
 var c=d.current,cs=st(c.weather_code);
 if(cs)b.classList.add('wx-'+cs);
 cur.innerHTML='<div class="wh">'+(cs?ic(cs,40):'')+'<div><div class="wn">'+Math.round(c.temperature_2m)+'°C<small>'+f(c.temperature_2m)+'°F</small></div>'+(cs?'<div class="ws">'+LB[cs]+'</div>':'')+'</div></div><div class="wd">Precipitation '+c.precipitation+' mm · Humidity '+c.relative_humidity_2m+'%</div><div class="wm">Click for 7-day forecast</div>';
 var y=d.daily,T=function(x){return x?x.slice(11,16):'–'},DL=function(sec){var m=Math.round(sec/60);return Math.floor(m/60)+' h '+(m%60<10?'0':'')+(m%60)+' min'};
 if(y.sunrise&&y.daylight_duration&&y.time.length>1){var dd=Math.round(y.daylight_duration[1]-y.daylight_duration[0]),ad=Math.abs(dd),dm=Math.floor(ad/60),dsx=ad%60,sg=dd>0?'+':(dd<0?'−':'±');
  cur.insertAdjacentHTML('beforeend','<div class="wd">Sunrise '+T(y.sunrise[1])+' · Sunset '+T(y.sunset[1])+'</div><div class="wd">Day length '+DL(y.daylight_duration[1])+' ('+sg+(dm?dm+' min ':'')+dsx+' s from yesterday)</div>');}
 var h='<table><tr><th>Day</th><th>High/Low</th><th>Rain</th><th>Hum.</th><th>Wind</th></tr>';
 for(var i=1;i<y.time.length;i++){var dt=new Date(y.time[i]+'T12:00:00');
  var ds=st(y.weather_code?y.weather_code[i]:null);
  h+='<tr><td>'+(ds?ic(ds,18):'')+dt.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'})+'</td><td>'+Math.round(y.temperature_2m_max[i])+'° / '+Math.round(y.temperature_2m_min[i])+'°C</td><td>'+(y.precipitation_probability_max[i]==null?'–':y.precipitation_probability_max[i]+'%')+' · '+y.precipitation_sum[i]+' mm</td><td>'+(y.relative_humidity_2m_mean?Math.round(y.relative_humidity_2m_mean[i])+'%':'–')+'</td><td>'+Math.round(y.wind_speed_10m_max[i])+' km/h '+dir(y.wind_direction_10m_dominant[i])+'</td></tr>'}
 tb.innerHTML=h+'</table>';
}).catch(fail);
})();
(function(){
var sf=document.getElementById('suggest');
if(sf){var mk=function(){var n=sf.sn.value.trim(),u=sf.su.value.trim(),t=sf.st.value.trim();
 return {t:'Add source: '+n,b:'URL: '+u+'\n\nNote: '+(t||'(none)')}};
 sf.addEventListener('submit',function(ev){ev.preventDefault();var m=mk();
  window.open('https://github.com/tomgassistant-png/desk/issues/new?labels=source&title='+encodeURIComponent(m.t)+'&body='+encodeURIComponent(m.b),'_blank','noopener')});
 document.getElementById('smail').addEventListener('click',function(ev){var m=mk();if(!sf.sn.value.trim())return;
  this.href='mailto:tomji@mail.grokbot.com?subject='+encodeURIComponent(m.t)+'&body='+encodeURIComponent(m.b)})}
})();
(function(){
var f=document.getElementById('search'),q=document.getElementById('q'),r=document.getElementById('results'),idx=null,pend=false;
if(!f||!window.fetch)return; f.hidden=false;
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function load(){if(idx||pend)return;pend=true;fetch('search-index.json',{cache:'no-cache'}).then(function(x){return x.json()}).then(function(d){idx=d.items.map(function(it){it._t=[it.headline,it.summary,it.source,it.section_name,it.date,it.edition,it.date_long].join(' ').toLowerCase();return it});run()}).catch(function(){r.hidden=false;r.innerHTML='<h2>Search</h2><p class="empty">The search index could not be loaded.</p>'})}
function run(){var v=q.value.trim().toLowerCase();
 if(!v){document.body.classList.remove('searching');r.hidden=true;r.innerHTML='';return}
 document.body.classList.add('searching');r.hidden=false;
 if(!idx){r.innerHTML='<h2>Searching…</h2>';load();return}
 var w=v.split(/\s+/),m=idx.filter(function(it){return w.every(function(x){return it._t.indexOf(x)>=0})});
 var h='<h2>'+m.length+' result'+(m.length==1?'':'s')+' for “'+esc(q.value.trim())+'”</h2>';
 if(!m.length)h+='<p class="empty">No stories match. Clear the box to return to the front page.</p>';
 m.forEach(function(it){h+='<article class="story'+(it.new?' new':'')+'"><p class="sec">'+esc(it.section_name)+'</p><h3><a href="'+esc(it.url)+'" rel="noopener" target="_blank">'+(it.new?'<span class="tag-new">New</span>':'')+esc(it.headline)+'</a></h3><p class="summary">'+esc(it.summary)+'</p><p class="meta"><span class="src">'+esc(it.source)+'</span> · '+esc(it.date_long)+' · '+esc(it.edition_long)+' edition</p></article>'});
 r.innerHTML=h}
q.addEventListener('focus',load);q.addEventListener('input',run);
document.getElementById('qclear').addEventListener('click',function(){q.value='';run();q.focus()});
q.addEventListener('keydown',function(ev){if(ev.key==='Escape'){q.value='';run()}});
})();
"""

def search_index(data, now):
    newest = max(it["edition"] for it in data["items"])
    items = sorted(data["items"], key=lambda it: (it["date"], it["published"]), reverse=True)
    keys = ["id", "edition", "date", "section", "headline", "summary", "source", "url"]
    return {"built": now.isoformat(timespec="minutes"), "count": len(items),
            "items": [dict({k: it[k] for k in keys}, section_name=SECTIONS[it["section"]],
                           date_long=long_date(it["date"]), edition_long=long_date(it["edition"]),
                           new=it["edition"] == newest) for it in items]}

def sources_html():
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
    except FileNotFoundError:
        d = {"sources": []}
    src = d.get("sources", [])
    groups = list(d.get("groups", []))
    for s in src:
        if s.get("group", "Other") not in groups:
            groups.append(s.get("group", "Other"))
    h = ['<div class="sources" id="sources"><h2>Sources we check</h2>']
    for g in groups:
        xs = [s for s in src if s.get("group", "Other") == g]
        if not xs:
            continue
        h.append(f'<h4>{e(g)}</h4><ul>')
        for s in xs:
            note = f'<span class="s">{e(s["note"])}</span>' if s.get("note") else ""
            h.append(f'<li><a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s["name"])}</a>{note}</li>')
        h.append('</ul>')
    h.append('<form class="suggest" id="suggest"><h3>Suggest a source</h3>'
             '<input name="sn" placeholder="Name" required aria-label="Source name">'
             '<input name="su" type="url" placeholder="https://" required aria-label="Source URL">'
             '<textarea name="st" rows="2" placeholder="Note (optional)" aria-label="Note"></textarea>'
             '<button type="submit">Submit on GitHub</button>'
             '<p class="alt">No GitHub account? <a id="smail" href="mailto:tomji@mail.grokbot.com?subject=Add%20source">Send it by email</a> instead.</p></form></div>')
    return "".join(h)

DEFAULT_WEATHER = {"name": "Herzliya", "lat": 32.1663, "lon": 34.8436, "timezone": "Asia/Jerusalem"}

def weather_html(data):
    import html as _h
    loc = dict(DEFAULT_WEATHER, **(data.get("weather_location") or {}))
    return ('<details class="wx" id="wx" data-loc="' + _h.escape(json.dumps(loc), quote=True) + '"><summary>'
            '<div class="wl">Weather · ' + _h.escape(loc["name"]) + '</div><div id="wxcur"><div class="wd">Loading weather…</div></div></summary>'
            '<div id="wxtab"></div><div class="src">Data: Open-Meteo</div></details>'
            '<div class="wxlink" style="font-family:Helvetica,Arial,sans-serif;font-size:13px;margin:-16px 0 22px"><a href="https://ims.gov.il/en/cityPortal?lid=240" target="_blank" rel="noopener">Open the IMS forecast for Apollonia &rarr;</a></div>')

def build(data, now):
    global NEWEST
    items = data["items"]
    validate(items)
    NEWEST = max(it["edition"] for it in items)
    n_front = 1
    n_hl = int(data.get("highlight_count", 8))
    n_latest = int(data.get("latest_count", 8))
    order = {it["id"]: i for i, it in enumerate(items)}
    editions = sorted({it["edition"] for it in items}, reverse=True)
    front_ed = {d for d in editions if d[:10] == editions[0][:10]} if editions else set()
    front = [it for it in items if it["edition"] in front_ed]
    by_new = lambda xs: sorted(xs, key=lambda it: (pub(it), -order[it["id"]]), reverse=True)

    lead = next((it for it in by_new(front) if it.get("lead")), None) or \
           next((it for it in by_new(front) if it["section"] == "pa"), by_new(front)[0])

    def latest_list(n):
        parts = ['<ol>']
        for it in by_new(front)[:n]:
            t = pub(it)
            parts.append(f'<li class="{nc(it).strip()}"><span class="time">{t.day} {t:%b} · {t:%H:%M}</span>'
                         f'<a class="h" href="#{e(it["id"])}">{tag(it)}{e(it["headline"])}</a>'
                         f'<span class="s">{e(it["source"])}</span></li>')
        parts.append('</ol>')
        return "".join(parts)

    title = data.get("title", "Judea & Samaria Desk")
    sub = data.get("subtitle", "")
    out = []
    out.append(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
               f'<meta name="robots" content="noindex, nofollow, noarchive"><meta name="viewport" content="width=device-width, initial-scale=1">'
               f'<title>{e(title)} — {e(long_date(now.date()))}</title>'
               f'<meta name="description" content="{e(sub)}"><style>{CSS}{NAV_CSS}</style></head><body><div class="page">' + __import__('sitenav').nav('jsd', '', ' | <a href="#backgrounders">Backgrounders</a>'))
    out.append(f'<div class="topline"><span>Compiled from the daily PA security letters</span>'
               f'<span>Updated {now:%H:%M} Israel time</span></div>')
    out.append(f'<header class="masthead"><h1>{e(title)}</h1><p class="sub">{e(sub)}</p>'
               '<form class="search" id="search" role="search" hidden onsubmit="return false">'
               '<input type="search" id="q" placeholder="Search all editions" aria-label="Search all editions" autocomplete="off">'
               '<button type="button" id="qclear">Clear</button></form></header>')
    span = long_date(editions[0]) if editions else ''
    out.append(f'<div class="dateline"><span>{e(weekday_date(now.date()))}</span>'
               f'<span>Jerusalem</span><span>This edition: {e(span)}{e(" · " + data["interim_label"]) if editions and data.get("interim_label") and editions[0].endswith("-pm") else ""}</span></div>')

    out.append('<section class="results" id="results" hidden aria-live="polite"></section>')
    out.append('<div class="layout"><main class="main">')
    out.append(f'<section class="lead{nc(lead)}" id="{e(lead["id"])}"><p class="kicker">{e(SECTIONS[lead["section"]])}</p>'
               f'<h2><a href="{e(lead["url"])}" rel="noopener" target="_blank">{tag(lead)}{e(lead["headline"])}</a></h2>'
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
            sv.append(f'<li class="{nc(it).strip()}"><a class="h" href="{e(it["url"])}" rel="noopener" target="_blank">{tag(it)}{e(it["headline"])}</a>'
                      f'<span class="s">{e(it["source"])} · {e(long_date(it["date"]))}</span></li>')
        sv.append('</ol>')
    sv.append('</div>')
    out.append('<aside class="rail">' + "".join(sv) + '<div class="sources" id="backgrounders"><h2>Backgrounders</h2><ul><li><a href="beit-hanina/">Beit Hanina: historical and contemporary profile</a></li><li><a href="maozim/">The Ma\'ozim Road (Beitunia bypass) and the Wallerstein Road</a></li><li><a href="trump-plan-settlers/">Why settler leaders opposed the Trump plan (2020)</a></li><li><a href="taybeh/">Taybeh: historical and contemporary profile</a></li><li><a href="abu-falah/">Abu Falah, October 16, 2026: the Israeli account and the evidence</a></li><li><a href="belgian-consul/">The Belgian Consul General in Jerusalem</a></li><li><a href="jonathan-pollak/">Jonathan Pollak: activist profile</a></li><li><a href="huckabee/">Ambassador Huckabee and "settler violence": statements and visits</a></li><li><a href="khamaisi/">The "Khamaisi Plan": Galilee planning, with maps</a></li></ul><h2>Sections</h2><ul><li><a href="yemen/">Yemen Desk: the daily anti-Houthi campaign brief</a></li></ul></div>' + sources_html() + '<div class="about"><strong>About this page.</strong> Every item is taken from the morning '
               'letters and evening supplements on the Palestinian Authority and security, and links to its '
               'original source. Times are Israel time.</div></aside></div>')

    out.extend(hl_html)
    out.append('<section class="archive"><h2>Archive — earlier editions</h2>')
    if not older:
        out.append('<p class="empty">No earlier days yet.</p>')
    for i, d in enumerate(older):
        day = [it for it in items if it["edition"] == d]
        day.sort(key=lambda it: (list(SECTIONS).index(it["section"]), order[it["id"]]))
        out.append(f'<details><summary>{e(weekday_date(date.fromisoformat(d[:10])))}'
                   f'<span class="n">{len(day)} items</span></summary><div class="day">')
        for it in day:
            out.append(f'<article class="story" id="{e(it["id"])}"><p class="sec">{e(SECTIONS[it["section"]])}</p>'
                       f'<h3><a href="{e(it["url"])}" rel="noopener" target="_blank">{e(it["headline"])}</a></h3>'
                       f'<p class="summary">{e(it["summary"])}</p>{meta(it)}</article>')
        out.append('</div></details>')
    out.append('</section>')
    out.append(f'<footer>{e(title)} · {len(items)} items on file · built {now:%d %B %Y, %H:%M} Israel time</footer>')
    out.append('</div><script>' + JS + '</script></body></html>')
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
    import os
    ip = os.path.join(os.path.dirname(os.path.abspath(a.out)), "search-index.json")
    json.dump(search_index(data, now), open(ip, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {ip}")
    print(f"wrote {a.out}: {len(data['items'])} items")
