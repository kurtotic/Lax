# Lax

A recruiting notebook for **NCAA women's lacrosse**. Search Division I, II, and III programs, filter by academics and location, save dated notes on each school, and keep a ranked target list.

Built for a family that wants one calm place to compare programs — not another generic spreadsheet.

## Run locally

```bash
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173).

Production build:

```bash
npm run build
npm run preview
```

No login. Notes and the target ranking are stored in the browser (`localStorage`) so they survive refresh.

## What you can do

- Browse **562** women's lacrosse programs (132 D1, 127 D2, 303 D3).
- Free-text search across school, city, state, conference, nickname, and coach.
- Filter by division, region, state, conference, public/private, campus setting, enrollment, and SAT mid-range. Acceptance rate, tuition, and retention use range sliders on the front page (in-state or out-of-state tuition).
- Open a school page for academics, program info, and a notes timeline (newest first, with relative time and exact timestamp).
- Open **Notes** to see every comment, newest first, filtered by school or date.
- Flag target schools and reorder them with drag-and-drop or up/down arrows. Rank persists. Download or restore a localStorage backup from the targets page.

Example path: search **Boston College** → open the school → add a note such as *Emailed Boston College coach with file and tournament schedule.*

## Data

School names, locations, public/private, conference, division, enrollment, admit rate, SAT range and mean, test policy, graduation rate, retention, coach, and coach email come from `scripts/schools_from_sheet.csv` (a Google Sheet export). Empty cells stay empty and show as “Not listed.” The catalog does not estimate tuition, campus setting, nicknames, or NCAA totals.

Schools that were already on the site but are not in the sheet stay listed by name, division, conference, and location, with coach and stat fields cleared, so older saved notes can still open them.

Rebuild the catalog after editing the sheet:

```bash
npm run generate:data
```

## Stack

Vite, React, TypeScript, Tailwind CSS, React Router, [@dnd-kit](https://dndkit.com) for the target board.
