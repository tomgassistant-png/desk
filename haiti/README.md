Haiti tracker. Edit haiti/make_data.py (it writes haiti/data.json), then run: python3 haiti/make_data.py && python3 build_haiti.py, then publish.
Rules from Tom: title "Crushing the Serpent Under the Heel", no subtitle, no grading; each item has who/where/when/evidence and "Another source says"; "crush" in our voice; "Gang Suppression Force" only as a proper name; never "mercenaries" outside a quotation or a source's own title.

## Map links (25 Oct 2026, Tom's request)
build_haiti.py adds a "Map:" line of Google Maps links to every feed item, summary, section bullet and gang entry that names a place listed in haiti/places.json (coordinates from OpenStreetMap Nominatim). Matching is by place name, ignoring accents and hyphens. To map a new place, add it to places.json with lat, lon and optional note; check the point first (areas such as Cul-de-Sac and Canaan are left out because no single sourced point fits). Never invent coordinates.
