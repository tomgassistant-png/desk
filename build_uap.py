#!/usr/bin/env python3
"""Build uap/index.html: the UAP hub page (links to the UFO Researcher Network map, the podcast feed and backgrounders; news feeds to come)."""
import os, sitenav
from datetime import datetime
from build import CSS, TZ
D = os.path.dirname(os.path.abspath(__file__))
CARDS = [
 ("UFO Researcher Network", "../ufo-network/", "A map of the people who study UFOs and UAPs, from scientists and scholars to investigators, and how they connect."),
 ("UFO, AI &amp; Folklore Podcast Feed", "../ufo-podcasts/", "The best recent podcast episodes on Jacques Vallee, D.W. Pasulka, folklore, and ideas linking AI and aliens. Refreshed daily at about 4 a.m. Israel time."),
 ("Backgrounder: Frank Salisbury and the Uintah Basin sightings", "../uinta/", "The plant physiologist who investigated the 1960s and 1970s wave of UFO reports in northeastern Utah. It is a section of the Uinta Mountains trip page; scroll to \u201cThe UFO angle.\u201d"),
]
def build(now):
    cards = "".join(f'<article class="story"><h3><a href="{u}">{t}</a></h3><p class="summary">{d}</p></article>' for t, u, d in CARDS)
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>UAP Desk</title>'
            f'<style>{CSS}</style></head><body><div class="page">{sitenav.nav("uap", "../")}'
            '<header class="masthead"><h1>UAP Desk</h1><p class="dateline">UFOs, UAPs, the people who study them, and where AI comes in</p></header>'
            f'<h2 class="edn">Reference</h2>{cards}'
            '<h2 class="edn">News feeds</h2><p class="summary"><i>Coming soon. News on UAP hearings, disclosure, research and sightings will appear here.</i></p>'
            f'<p class="srcs">Page built {now:%d %B %Y, %H:%M} Israel time.</p></div></body></html>')
if __name__ == "__main__":
    open(os.path.join(D, "uap/index.html"), "w", encoding="utf-8").write(build(datetime.now(TZ)))
    print("wrote uap/index.html")
