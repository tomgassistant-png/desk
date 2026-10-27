"""Shared section nav for the cover, JSD, Yemen and digest pages.
Each link carries data-sec and data-upd (latest update date, embedded at build time).
Browser JS compares data-upd with localStorage 'seen:<sec>' and shows unseen sections in bold #9b1c1c."""
import json, os, html
ROOT = os.path.dirname(os.path.abspath(__file__))
e = lambda s: html.escape(str(s), quote=True)

def _load(p):
    p = os.path.join(ROOT, p)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def load_digest():
    """digest/items.json plus the Drinks Advisor section (digest/drinks-advisor/section.json, owned by the Drinks Advisor assistant)."""
    d = _load("digest/items.json")
    for owned in ("drinks-advisor", "scholar"):
        x = _load(f"digest/{owned}/section.json")
        if x.get("section") and d.get("sections") is not None:
            d["sections"] = [s for s in d["sections"] if s["id"] != x["section"]["id"]] + [x["section"]]
            d["items"] = d.get("items", []) + x.get("items", [])
    return d

def sections():
    """[(id, path-from-root, name, latest date or '')]"""
    jsd = _load("items.json").get("items", [])
    ye = _load("yemen/items.json").get("editions", [])
    d = load_digest()
    out = [("jsd", "", "Judea &amp; Samaria", max((i["edition"] for i in jsd), default="")),
           ("yemen", "yemen/", "Yemen", max((x["date"] for x in ye), default=""))]
    for s in d.get("sections", []):
        dt = max([i["edition"] for i in d.get("items", []) if i["section"] == s["id"]] + ([s["updated"]] if s.get("updated") else []), default="")
        out.append((s["id"], f'digest/{s["id"]}/', e(s["name"]), dt))
    return out

CSS = ('.secnav a.unseen{color:#9b1c1c;font-weight:700}')
JS = ("<script>(function(){try{var S=localStorage;document.querySelectorAll('nav.secnav a[data-sec]').forEach(function(a){"
      "var k='seen:'+a.dataset.sec,u=a.dataset.upd||'';"
      "if(a.classList.contains('on')){if(u)S.setItem(k,u);return}"
      "if(u&&(S.getItem(k)||'')<u)a.classList.add('unseen');"
      "a.addEventListener('click',function(){if(u)S.setItem(k,u);a.classList.remove('unseen')});});}catch(x){}})();</script>")

def nav(here, root, extra=""):
    links = [f'<a href="{root}cover/"{" class=on" if here == "cover" else ""}>Cover</a>']
    for k, p, name, dt in sections():
        links.append(f'<a href="{root}{p}" data-sec="{k}" data-upd="{dt}"{" class=on" if k == here else ""}>{name}</a>')
    _hd = _load("horses/data.json").get("updated", "")
    links.append(f'<a href="{root}horses/" data-sec="horses" data-upd="{_hd}"{" class=on" if here == "horses" else ""}>Horses</a>')
    _hz = _load("haiti/data.json").get("updated", "")[:10]
    links.append(f'<a href="{root}haiti/" data-sec="haiti" data-upd="{_hz}"{" class=on" if here == "haiti" else ""}>Haiti</a>')
    _ms = _load("mars/data.json").get("updated", "")[:10]
    links.append(f'<a href="{root}mars/" data-sec="mars" data-upd="{_ms}"{" class=on" if here == "mars" else ""}>Mars</a>')
    return f'<style>{CSS}</style><nav class="secnav">' + " | ".join(links) + extra + '</nav>' + JS
