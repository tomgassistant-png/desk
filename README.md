# Judea & Samaria Desk: front page generator

Files
- `items.json`: all stories (the only file you edit day to day)
- `build.py`: renders `items.json` into `index.html` (Python 3.9+, no extra packages)
- `index.html`: self-contained page (inline CSS, a few lines of inline vanilla JavaScript for search, no external files)
- `search-index.json`: written by `build.py` on every build; every item (headline, summary, source, section, dates, link), newest first. `publish.sh` copies it to the site, so the daily update refreshes it.
- `preview-desktop.png`, `preview-mobile.png`: screenshots

## How the page is assembled
- **Front page** = only the newest `edition` in items.json (today's letter). Sections with no items in that edition are hidden.
- **Highlights from previous editions** = at the bottom, just above the archive: a one-line list (headline linked to source, outlet, edition date) of up to `highlight_count` (default 8) earlier stories marked `"highlight": true`, newest edition first. If an earlier edition has none marked, its lead plus one more item (PA section preferred) are used.
- **Saved stories** = every item with `"saved": true` (optional `"saved_on": "YYYY-MM-DD"`, used for ordering, newest first), shown permanently at the top of the side column (on phones the side column follows the main stories). Saved items never age out; they still also appear in their own edition or the archive. With none saved it shows "No saved stories yet."
- **Archive** = every earlier edition, grouped by day, all folded, so nothing is lost. No story is shown twice on the visible page.
- **Lead story** = the newest front-page item with `"lead": true`. If there is none, the newest item in the `pa` section is used. Set `lead` on one item per day and remove it from the previous day's item, or leave it there; the newest one always wins.
- **Latest** column = the `latest_count` newest items of the current edition by `published` time (5 on phones).
- Sections (`section` key): `pa` Palestinian Authority forces and the threat · `attacks` Attacks and incidents · `land` Settlement and land · `idf` IDF and government decisions · `negev` Negev and Galilee.

## Search
New stories: every item whose `edition` equals the newest edition in `items.json` (i.e. added in the latest daily update) gets the CSS class `new` at build time: dark red headline (#9b1c1c) and a small uppercase "New" tag before it, in the lead, sections, Latest column, Saved stories and search results (`search-index.json` carries `"new": true`). When the next edition is added they go back to black automatically. No JavaScript needed except in search results.

A search box under the masthead searches every item in `search-index.json` (current and past editions), entirely in the browser: case-insensitive, all words must match (headline, summary, source, section, date). Results are newest first with a count; clearing the box (or Esc) restores the normal page. Without JavaScript the box is hidden and the page works as before. Search needs the page served over http(s) (e.g. `python3 -m http.server`), not file://.

## Adding a day
1. For each story in the day's letter (morning letter or evening supplement), append an object to `items`:
```json
{
  "id": "2026-10-10-short-slug",          // unique
  "edition": "2026-10-10",                 // the letter's date; this groups the archive
  "published": "2026-10-10T07:55:00+03:00",// when the letter went out (Israel time)
  "letter": "PA security: 10 Oct 2026",    // the subject of the source letter (not shown)
  "section": "pa",
  "lead": true,                            // optional
  "saved": true, "saved_on": "2026-10-10",  // optional: keep permanently in Saved stories
  "highlight": true,                       // optional: list it in Highlights once it is no longer the current edition
  "headline": "...",
  "summary": "Two or three plain sentences.",
  "source": "Arutz 7",                     // outlet named in the letter
  "date": "2026-10-09",                    // date of the report or event
  "url": "https://..."                     // the letter's link, without the google.com/url wrapper
}
```
2. Rebuild: `python3 build.py` (add `--now 2026-10-10T07:50` to fix the date line for a test build).
3. Optional screenshots:
```
google-chrome --headless=new --no-sandbox --hide-scrollbars --window-size=1280,3000 --screenshot=preview-desktop.png file://$PWD/index.html
google-chrome --headless=new --no-sandbox --hide-scrollbars --window-size=390,2600 --force-device-scale-factor=2 --screenshot=preview-mobile.png file://$PWD/index.html
```
`build.py` stops with a list of problems if a required field is missing, a section key is wrong, or an id repeats.

## Sources blogroll and suggestions
- The right-rail "Sources we check" list is built from `sources.json` (`groups` order, then `sources`: `name`, `url`, `group`, optional `note`). Routines may append entries; then rebuild and publish.
- "Suggest a source" on the page opens a prefilled GitHub issue on `tomgassistant-png/desk` with label `source` (title `Add source: <name>`, body with URL and note), or an email to tomji@mail.grokbot.com.
- Daily update: run `gh issue list -R tomgassistant-png/desk -l source -s open`. For each issue, add the source to `sources.json` (choose a fitting group), start checking it in the morning letter, rebuild, publish, then `gh issue close <n> -R tomgassistant-png/desk -c "Added to sources."`. gh is signed in as tomgassistant-png.

## Yemen section (/desk/yemen/)
Hidden from search engines (robots/googlebot noindex, nofollow, noarchive). Data: `yemen/items.json`; builder: `build_yemen.py` (imports CSS and helpers from `build.py`). Newest edition on top; earlier editions collapse into the archive. Section nav bar at the top of both pages: Judea & Samaria | Yemen | Backgrounders.

Daily Yemen routine, after the "Yemen campaign: <date>" email is sent:
1. Prepend one edition to `editions` in `yemen/items.json`:
   `{"date":"YYYY-MM-DD","lede":"opening line","items":[{"headline":"...","text":"the bullet, plain American English","source":"outlet named","link":"https://... or empty"}],"trend":"...","watch":"..."}`.
   Use the direct URL, without the google.com/url wrapper. One entry per date; replace it if the date already exists.
2. `cd /workspace/frontpage && python3 build_yemen.py`
3. `./publish.sh` (retry up to 3 times on TLS errors). It copies `yemen/` and keeps `beit-hanina/`.
4. Check that `curl -s -o /dev/null -w '%{http_code}' https://tomgassistant-png.github.io/desk/yemen/` returns 200.

## Cover and digest sections

The personal cover page is at `cover/` (https://tomgassistant-png.github.io/desk/cover/). Each daily research digest topic has a section page with an archive at `digest/<section-id>/`. JSD (`/desk/`) and Yemen (`/desk/yemen/`) are sections beside them; every page carries noindex, nofollow, noarchive.

Daily steps (digest routine, about 5:00 AM Israel time):
1. Append today's stories to `digest/items.json` → `items`. One object per story:
   `{"id": "YYYY-MM-DD-<section>-<n>", "edition": "YYYY-MM-DD", "section": "<section id>", "headline": "...", "lead": "first sentence", "text": "full paragraph, plain American English", "sources": [{"name": "Haaretz", "url": "https://... (real URL, not a google.com/url redirect)"}]}`
   Never delete old items; they form the archive. Stories in the newest edition get the dark red headline and NEW tag.
2. Add `editions["YYYY-MM-DD"] = {"intro": "...", "quiet": "Nothing material on ..."}` (optional but shown on the cover).
3. A new topic needs a new entry in `sections` (`{"id": "slug", "name": "Display name"}`); it then appears in every nav bar.
4. Run `python3 build_cover.py` (after the JSD and Yemen builds, so their "new today" lines are current), then publish:
   `cd /workspace/frontpage && for i in 1 2 3; do ./publish.sh && break; sleep 10; done`
