#!/usr/bin/env python3
"""Build yemen/taiz/index.html from yemen/taiz/update.md (the weekly Taiz update). Usage: python3 build_taiz.py"""
import os, re, markdown
from datetime import datetime
from build import CSS, TZ, e, long_date
from build_yemen import NAV_CSS

D = os.path.dirname(os.path.abspath(__file__))
FIG = ('.tz{max-width:900px;margin:0 auto}.tz table{border-collapse:collapse;width:100%;font-size:14px;margin:10px 0}'
       '.tz th,.tz td{border:1px solid #ccc;padding:5px 7px;vertical-align:top;text-align:left}.tz th{background:#f2f2f2}'
       '.tz figure{margin:14px 0;border-top:1px solid #ccc;padding-top:10px}.tz figure img{max-width:100%;height:auto;display:block;border:1px solid #ccc}'
       '.tz figcaption{font-size:13px;color:#333;margin-top:6px;line-height:1.4;font-family:Helvetica,Arial,sans-serif}'
       '.tz h1{font-size:30px}.tz h2{border-top:1px solid #222;padding-top:8px;margin-top:26px}.tz td{word-break:break-word}')

def figures(md):
    pat = re.compile(r'^\d\. \*\*`([^`]+)`\*\* — (.*)$', re.M)
    return pat.sub(lambda m: f'<figure markdown="1">\n<a href="images/{m.group(1)}"><img src="images/{m.group(1)}" alt="" loading="lazy"></a>\n<figcaption markdown="1">{m.group(2)}</figcaption>\n</figure>\n', md)

def build(now):
    md = open(os.path.join(D, "yemen/taiz/update.md"), encoding="utf-8").read()
    md = figures(md)
    body = markdown.markdown(md, extensions=["tables", "md_in_html"])
    body = body.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')
    nav = __import__("sitenav").nav("yemen", "../../")
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="robots" content="noindex, nofollow, noarchive"><meta name="googlebot" content="noindex, nofollow, noarchive">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>Battle for Taiz: weekly update — Yemen Desk</title>'
            f'<style>{CSS}{NAV_CSS}{FIG}</style></head><body><div class="page">{nav}'
            f'<div class="topline"><span><a href="../">← Yemen Desk</a></span><span>Page built {now:%d %B %Y, %H:%M} Israel time</span></div>'
            f'<main class="tz">{body}</main>'
            '<footer>Yemen Desk · weekly Taiz update · <a href="../">Back to the Yemen Desk</a></footer></div></body></html>')

if __name__ == "__main__":
    open(os.path.join(D, "yemen/taiz/index.html"), "w", encoding="utf-8").write(build(datetime.now(TZ)))
    print("wrote yemen/taiz/index.html")
