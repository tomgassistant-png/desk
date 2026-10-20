# Daily research digest, edition 2026-10-20 (Tuesday) — research brief for a helper

You research a set of digest sections for Tom Goldberger's personal cover page (https://tomgassistant-png.github.io/desk/cover/).
DO NOT edit /workspace/frontpage/digest/items.json, do not run any build or publish script, and do not send any email or message.
Write your results ONLY to the output JSON file named in your task.

## What to report
- Only what is NEW since the last edition (items with edition 2026-10-20; read them in
  /workspace/frontpage/digest/items.json, and skim 2026-10-17/18 too, plus the 2026-10-20 "quiet" note in editions) AND that changes the picture. Skip repeats.
- Window: roughly the early morning of 19 Oct 2026 through now (early morning 20 Oct 2026, Israel time, UTC+3).
- Check each specific fact (figures, dates, places, names, poll numbers) against a second source independent of Wikipedia.
  If you cannot, write "(unconfirmed)" or "according to X; not independently confirmed" in the text.
- Plain American English (center, not centre), no idioms, no hot takes. Attribute claims and analysis to named sources.
- Real source URLs only (the article pages you actually read), never google.com/url redirects. Never invent anything.
- Prefer primary reporting and named sources. Use WebSearch/WebFetch (cursor namespace) and the x namespace tools (public X search,
  25 results max per call, 30 calls/min) for X posts. sources.json in /workspace/frontpage has curated source lists (keys: groups, sources).
- Proportion: 0 to 4 items per section; a quiet section gets no item and is listed in "quiet".

## Item format (exactly as in README.md "Cover and digest sections")
{"id": "2026-10-20-<section-id>-<n>", "edition": "2026-10-20", "section": "<section id>", "headline": "...",
 "lead": "first sentence of text", "text": "full paragraph, plain American English",
 "sources": [{"name": "Outlet", "url": "https://..."}]}
(Look at existing items for the house style; some items may also carry optional fields like "image" — copy the existing pattern if you use one.)

## Baselines
Sections carney-case, trenton and france-election have "baseline", "baseline_sources" ([{label,url}]) and "baseline_updated"
in the sections list of items.json. If a development changes the basic picture, ALSO provide a rewritten baseline stating the
current position (keep the same structure/type as the existing one — france-election's baseline is a list of paragraphs),
updated baseline_sources, and baseline_updated "20 October 2026". Keep single-source points marked unconfirmed. Otherwise omit.

## Output file JSON shape
{"items": [...], "baselines": {"<section-id>": {"baseline": ..., "baseline_sources": [...], "baseline_updated": "20 October 2026"}},
 "quiet": ["<section-id>", ...], "quiet_notes": {"<section-id>": "optional short note, e.g. what is still pending"},
 "intro_phrases": ["short noun phrase per main story, for the edition intro, e.g. 'a new Ifop poll with Le Pen at 32 percent'"]}
Validate the file with python3 -c "import json;json.load(open(PATH))" before finishing.

## Report back
A short summary: items written per section, baselines changed, quiet sections, and anything you could not verify or reach.

## Section-specific standing orders (from Tom)
- lebanon: standing watch on Israeli reactions (official and unofficial) to the EU Support Mission in Lebanon (EUSM Lebanon, established 12 Oct 2026), in Hebrew and English Israeli press: Ynet, Maariv, Israel Hayom, Haaretz, Kan, Channel 12/N12, Channel 14, Times of Israel, JNS, and Israeli Foreign Ministry, PMO and IDF statements. Report each NEW reaction once, with its source, plus any news on which countries will contribute forces. Put a note under quiet_notes key "lebanon-eusm" either way. The Israel–Lebanon military meeting in Tampa was due to start 20 Oct.
- trenton: only news about the CITY of Trenton, NJ (not state news). Good news: economic recovery, development, investment, new businesses, housing, safety, residents' lives. Use the "Trenton (city)" sources in sources.json (local outlets, the city's site and Facebook page, local groups on X and Facebook). Add a reusable photo per story where possible (Wikimedia Commons or official photos, saved under /workspace/frontpage/digest/trenton/img/ with credit; copy the image-field pattern used by existing trenton items); link to news photos rather than copying them.
- france-election: run like Brazil. French outlets and pollsters first (Le Monde, Le Figaro, Libération, Les Échos, France Info, BFMTV, Le Parisien, L'Opinion, Politico Europe, Ifop, Elabe, Ipsos, Odoxa, Toluna, OpinionWay) plus candidates' X accounts. Report any new poll with pollster and date, and Polymarket odds when they move (previous snapshot: /workspace/frontpage/digest/polymarket_next-french-presidential-election.json; refresh it if you fetch new odds). Events affecting French politics: government stability, censure motions, budget, candidate moves, court rulings. Every day also cover street protests, strikes, school and university blockades and riots: scale (police and organizer counts), violence, arrests, groups and parties involved, government response, opinion polls, and attributed analysis of the effect on the 2027 election, using French media and French X posts. Tom calls the students "so-called students" — you may use the phrase "so-called students" once where natural, but keep reporting factual and attributed.
- spacex-xai-and-cursor: also covers Grok Bot news, using the official Grok Bot changelog and other sources. SpaceX third-quarter results were due Tuesday 20 Oct (check whether released; quote_SPCX.json in digest/ is the stock snapshot).
- brazil: presidential runoff Lula vs. Flávio Bolsonaro; new polls with pollster and date, debates, Polymarket moves.
- israel-election: new polls with outlet/pollster and date, party moves.
