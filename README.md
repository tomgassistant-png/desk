# Judea & Samaria Desk: front page generator

Files
- `items.json`: all stories (the only file you edit day to day)
- `build.py`: renders `items.json` into `index.html` (Python 3.9+, no extra packages)
- `index.html`: self-contained page (inline CSS, no JavaScript, no external files)
- `preview-desktop.png`, `preview-mobile.png`: screenshots

## How the page is assembled
- **Front page** = the newest `front_page_editions` edition dates (default 3). Older editions go to the **Archive**, grouped by day (the newest archived day is open, the rest are folded).
- **Lead story** = the newest front-page item with `"lead": true`. If there is none, the newest item in the `pa` section is used. Set `lead` on one item per day and remove it from the previous day's item, or leave it there; the newest one always wins.
- **Latest** column = the `latest_count` newest items by `published` time (5 on phones).
- Sections (`section` key): `pa` Palestinian Authority forces and the threat · `attacks` Attacks and incidents · `land` Settlement and land · `idf` IDF and government decisions · `negev` Negev and Galilee.

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
