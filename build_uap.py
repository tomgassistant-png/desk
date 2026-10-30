#!/usr/bin/env python3
"""Build uap/index.html: the UAP hub page (links to the UFO Researcher Network map, the podcast feed and backgrounders; news feeds to come)."""
import os, sitenav
from datetime import datetime
from build import CSS, TZ
D = os.path.dirname(os.path.abspath(__file__))
CARDS = [
 ("UFO Researcher Network", "../ufo-network/", "A map of the people who study UFOs and UAPs, from scientists and scholars to investigators, and how they connect."),
 ("UFO, AI &amp; Folklore Podcast Feed", "../ufo-podcasts/", "The best recent podcast episodes on Jacques Vallee, D.W. Pasulka, folklore, and ideas linking AI and aliens. Refreshed daily at about 4 a.m. Israel time."),
 ("Backgrounder: Skinwalker Ranch", "../skinwalker/", "An explainer on the Utah ranch in the Uintah Basin, famous for UFO and paranormal reports, and the government-funded studies done there."),
 ("Backgrounder: Frank Salisbury and the Uintah Basin sightings", "../uinta/", "The plant physiologist who investigated the 1960s and 1970s wave of UFO reports in northeastern Utah. It is a section of the Uinta Mountains trip page; scroll to \u201cThe UFO angle.\u201d"),
    ("Backgrounder: Arthur C. Clarke", "../backgrounders/arthur-c-clarke/", "The science fiction writer and futurist, and where his ideas meet UFOs, aliens and AI."),
]
FEEDJS = """<script>(function(){var b=document.getElementById('uapfeed');if(!b||!window.fetch)return;
function esc(x){return String(x||'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function list(t,a){if(!a||!a.length)return '';var h='';a.forEach(function(i){h+='<article class="story"><p class="sec">'+esc(i.source)+(i.date?' · '+esc(i.date):'')+'</p><h3><a href="'+esc(i.url)+'" target="_blank" rel="noopener">'+esc(i.title)+'</a></h3>'+(i.note?'<p class="summary">'+esc(i.note)+'</p>':'')+'</article>'});return h}
fetch('../ufo-podcasts/feed.json',{cache:'no-cache'}).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(d){var a=d.items;if(!a){a=(d.web||[]).concat(d.podcasts||[]);a.sort(function(x,y){return String(y.date||'').localeCompare(String(x.date||''))})}var h=list('',a);if(h)b.innerHTML=h+'<p class="srcs">From the daily scan'+(d.updated?' of '+esc(d.updated):'')+'.</p>'}).catch(function(){});})();</script>"""
def build(now):
    side = "".join(f'<div style="margin:0 0 14px"><a href="{u}"><b>{t}</b></a><p class="srcs" style="margin:4px 0">{d}</p></div>' for t, u, d in CARDS)
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>UAP Desk</title>'
            f'<style>{CSS}.uapg{{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:28px}}@media(max-width:800px){{.uapg{{grid-template-columns:1fr}}}}.uapside{{border-left:1px solid #ccc;padding-left:18px}}</style></head><body><div class="page">{sitenav.nav("uap", "../")}'
            '<header class="masthead"><h1>UAP Desk</h1><p class="dateline">UFOs, UAPs, the people who study them, and where AI comes in</p></header>'
            '<div class="uapg"><main><h2 class="edn">News feeds</h2><div id="uapfeed"><p class="summary">The daily scan of podcasts, YouTube, Substack and blogs will appear here starting 31 October. For now, see the <a href="../ufo-podcasts/">UFO, AI &amp; Folklore Podcast Feed</a>.</p></div></main>'
            f'<aside class="uapside"><h2 class="edn">Backgrounders</h2>{side}</aside></div>'
            f'<p class="srcs">Page built {now:%d %B %Y, %H:%M} Israel time.</p></div>{FEEDJS}</body></html>')
if __name__ == "__main__":
    open(os.path.join(D, "uap/index.html"), "w", encoding="utf-8").write(build(datetime.now(TZ)))
    print("wrote uap/index.html")
