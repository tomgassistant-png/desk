# Daily research digest, edition 2026-10-19 (Monday) — research brief for a helper

You research a set of digest sections for Tom Goldberger's personal cover page (https://tomgassistant-png.github.io/desk/cover/).
DO NOT edit /workspace/frontpage/digest/items.json, do not run any build or publish script, and do not send any email or message.
Write your results ONLY to the output JSON file named in your task.

## What to report
- Only what is NEW since the last edition (items with edition 2026-10-18, including the evening update; read them in
  /workspace/frontpage/digest/items.json, and skim 2026-10-16/17 too) AND that changes the picture. Skip repeats.
- Window: roughly the evening of 18 Oct 2026 through now (early morning 19 Oct 2026, Israel time, UTC+3).
- Check each specific fact (figures, dates, places, names, poll numbers) against a second source independent of Wikipedia.
  If you cannot, write "(unconfirmed)" or "according to X; not independently confirmed" in the text.
- Plain American English (center, not centre), no idioms, no hot takes. Attribute claims and analysis to named sources.
- Real source URLs only (the article pages you actually read), never google.com/url redirects. Never invent anything.
- Prefer primary reporting and named sources. Use WebSearch/WebFetch (cursor namespace) and the x namespace tools (public X search,
  25 results max per call, 30 calls/min) for X posts. sources.json in /workspace/frontpage has curated source lists (keys: groups, sources).
- Proportion: 0 to 4 items per section; a quiet section gets no item and is listed in "quiet".

## Item format (exactly as in README.md "Cover and digest sections")
{"id": "2026-10-19-<section-id>-<n>", "edition": "2026-10-19", "section": "<section id>", "headline": "...",
 "lead": "first sentence of text", "text": "full paragraph, plain American English",
 "sources": [{"name": "Outlet", "url": "https://..."}]}
(Look at existing items for the house style; some items may also carry optional fields like "image" — copy the existing pattern if you use one.)

## Baselines
Sections carney-case, trenton and france-election have "baseline", "baseline_sources" ([{label,url}]) and "baseline_updated"
in the sections list of items.json. If a development changes the basic picture, ALSO provide a rewritten baseline stating the
current position (keep the same structure/type as the existing one — france-election's baseline is a list of paragraphs),
updated baseline_sources, and baseline_updated "19 October 2026". Keep single-source points marked unconfirmed. Otherwise omit.

## Output file JSON shape
{"items": [...], "baselines": {"<section-id>": {"baseline": ..., "baseline_sources": [...], "baseline_updated": "19 October 2026"}},
 "quiet": ["<section-id>", ...], "quiet_notes": {"<section-id>": "optional short note, e.g. what is still pending"},
 "intro_phrases": ["short noun phrase per main story, for the edition intro, e.g. 'a new Ifop poll with Le Pen at 32 percent'"]}
Validate the file with python3 -c "import json;json.load(open(PATH))" before finishing.

## Report back
A short summary: items written per section, baselines changed, quiet sections, and anything you could not verify or reach.
