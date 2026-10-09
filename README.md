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

- Browse **549** women's lacrosse programs (133 D1, 115 D2, 301 D3).
- Free-text search across school, city, state, conference, nickname, and coach.
- Filter by division, region, state, conference, public/private, campus setting, enrollment, and SAT mid-range. Acceptance rate, tuition, and retention use range sliders on the front page (in-state or out-of-state tuition).
- Open a school page for academics, program info, and a notes timeline (newest first, with relative time and exact timestamp).
- Open **Notes** to see every comment, newest first, filtered by school or date.
- Flag target schools and reorder them with drag-and-drop or up/down arrows. Rank persists. Download or restore a localStorage backup from the targets page.

Example path: search **Boston College** → open the school → add a note such as *Emailed Boston College coach with file and tournament schedule.*

## Data

Program names, cities, states, conferences, nicknames, and (for Division I) NCAA appearance/title counts are compiled from public lists:

- [Wikipedia: NCAA Division I lacrosse programs](https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_lacrosse_programs) (women's table, 2026/27 affiliations)
- [Wikipedia: NCAA Division II lacrosse programs](https://en.wikipedia.org/wiki/List_of_NCAA_Division_II_lacrosse_programs) (women's table)
- Public D3 directories (ProductiveRecruit D3 women's lacrosse listing)

**Academic stats** (enrollment, acceptance, retention, tuition, SAT/ACT) are approximate. Well-known schools use commonly published College Board / IPEDS-style ranges; remaining schools use stable estimated ranges so filters still work. They are for fit exploration, not official NCAA or registrar data. Confirm everything on the school's site before you apply.

**Head coaches** for flagship programs use commonly published staff names. Remaining coach names are placeholders so search still works — always verify on the athletics roster.

To regenerate `src/data/schools.json` after updating the Wikipedia dumps in `/tmp`:

```bash
npm run generate:data
```

## Stack

Vite, React, TypeScript, Tailwind CSS, React Router, [@dnd-kit](https://dndkit.com) for the target board.
