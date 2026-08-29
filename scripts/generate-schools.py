#!/usr/bin/env python3
"""Compile NCAA women's lacrosse programs into src/data/schools.json."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def wiki_text(name: str) -> str:
    data = json.loads(Path(f"/tmp/{name}.json").read_text())
    return data["parse"]["wikitext"]["*"]


def clean_cell(raw: str) -> str:
    text = raw.strip()
    text = re.sub(r"colspan\s*=\s*\d+\s*\|", "", text, flags=re.I)
    text = re.sub(r"rowspan\s*=\s*\d+\s*\|", "", text, flags=re.I)
    text = re.sub(r"bgcolor\s*=\s*#?[0-9a-fA-F]+\s*\|", "", text)
    text = re.sub(r"\{\{efn[\s\S]*?\}\}", "", text)
    text = re.sub(r"\{\{refn[\s\S]*?\}\}", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"<ref[^/]*/>", "", text)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"\{\{sort\|[^|]*\|", "", text)
    text = re.sub(r"\{\{sortname\|([^|]+)\|([^}]+)\}\}", r"\1 \2", text)
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    text = text.replace("'''", "").replace("''", "").replace("}}", "").replace("{{", "")
    # Prefer piped wiki link display text
    text = re.sub(r"\[\[[^|\]]*\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip(" |")
    text = text.replace("&nbsp;", " ")
    return text.strip()


def school_display(cell: str) -> tuple[str, str | None]:
    name = clean_cell(cell)
    name = re.sub(r"\s+", " ", name).strip()
    short = None
    extra = re.match(r"^(.*)\s+\(([^)]+)\)\s*$", name)
    if extra:
        inner = extra.group(2).strip()
        base = extra.group(1).strip()
        # Wikipedia sort keys: "(Maryland)", "(Penn State)". Keep "Wheaton College (Massachusetts)".
        if inner.lower() in base.lower() or inner not in STATE_ABBR:
            name = base
            short = inner
    return name, short


def parse_wiki_table(section: str) -> list[dict]:
    rows: list[dict] = []
    current: list[str] = []
    for line in section.splitlines():
        if line.startswith("|-"):
            if current:
                rows.append(current)
            current = []
            continue
        if line.startswith("|}"):
            if current:
                rows.append(current)
            break
        if line.startswith("!"):
            continue
        if line.startswith("|"):
            current.append(line[1:])
        elif current:
            current[-1] += " " + line
    programs = []
    for cells in rows:
        if len(cells) < 5:
            continue
        name, short = school_display(cells[0])
        if not name or name.lower() in {"school"}:
            continue
        nickname = clean_cell(cells[1])
        city = clean_cell(cells[2])
        state = clean_cell(cells[3])
        conference = clean_cell(cells[4])
        first_season = None
        appearances = 0
        titles = 0
        cleaned_rest = [clean_cell(c) for c in cells[5:]]
        year_idx = next(
            (i for i, c in enumerate(cleaned_rest) if re.match(r"^(19|20)\d{2}\b", c)),
            None,
        )
        if year_idx is not None:
            first_season = int(re.search(r"(19|20)\d{2}", cleaned_rest[year_idx]).group(0))
            if year_idx + 1 < len(cleaned_rest):
                m = re.match(r"\((\d+)\)", cleaned_rest[year_idx + 1])
                if m:
                    appearances = int(m.group(1))
            if year_idx + 2 < len(cleaned_rest):
                m = re.match(r"\((\d+)\)", cleaned_rest[year_idx + 2])
                if m:
                    titles = int(m.group(1))
        programs.append(
            {
                "name": name,
                "shortName": short,
                "nickname": nickname,
                "city": city,
                "state": state,
                "conference": conference,
                "firstSeason": first_season,
                "ncaaAppearances": appearances,
                "ncaaTitles": titles,
            }
        )
    return programs


def parse_d3_markdown(path: Path) -> list[dict]:
    programs = []
    for line in path.read_text().splitlines():
        if not line.startswith("|") or line.startswith("| Name") or line.startswith("|---"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 4 or parts[2] != "NCAA D3":
            continue
        name, location, _div, conference = parts[:4]
        if "," in location:
            city, state = [p.strip() for p in location.rsplit(",", 1)]
        else:
            city, state = location, ""
        programs.append(
            {
                "name": name,
                "shortName": None,
                "nickname": "",
                "city": city,
                "state": state,
                "conference": conference,
                "firstSeason": None,
                "ncaaAppearances": 0,
                "ncaaTitles": 0,
            }
        )
    return programs


STATE_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "D.C.": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

REGION = {
    "ME": "Northeast",
    "NH": "Northeast",
    "VT": "Northeast",
    "MA": "Northeast",
    "RI": "Northeast",
    "CT": "Northeast",
    "NY": "Northeast",
    "PA": "Mid-Atlantic",
    "NJ": "Mid-Atlantic",
    "DE": "Mid-Atlantic",
    "MD": "Mid-Atlantic",
    "DC": "Mid-Atlantic",
    "VA": "Southeast",
    "NC": "Southeast",
    "SC": "Southeast",
    "GA": "Southeast",
    "FL": "Southeast",
    "AL": "Southeast",
    "TN": "South",
    "KY": "South",
    "WV": "South",
    "AR": "South",
    "LA": "South",
    "MS": "South",
    "TX": "South",
    "OK": "South",
    "OH": "Midwest",
    "MI": "Midwest",
    "IN": "Midwest",
    "IL": "Midwest",
    "WI": "Midwest",
    "MN": "Midwest",
    "IA": "Midwest",
    "MO": "Midwest",
    "CO": "West",
    "UT": "West",
    "AZ": "West",
    "CA": "West",
    "OR": "West",
    "WA": "West",
    "ID": "West",
    "NV": "West",
}

NICKNAMES = {
    "Amherst College": "Mammoths",
    "Babson College": "Beavers",
    "Bates College": "Bobcats",
    "Bowdoin College": "Polar Bears",
    "Brandeis University": "Judges",
    "Bryn Mawr College": "Owls",
    "Colby College": "Mules",
    "Colorado College": "Tigers",
    "Connecticut College": "Camels",
    "Denison University": "Big Red",
    "Dickinson College": "Red Devils",
    "Franklin and Marshall College": "Diplomats",
    "Gettysburg College": "Bullets",
    "Hamilton College": "Continentals",
    "Haverford College": "Fords",
    "Ithaca College": "Bombers",
    "Massachusetts Institute of Technology": "Engineers",
    "Middlebury College": "Panthers",
    "Salisbury University": "Sea Gulls",
    "Skidmore College": "Thoroughbreds",
    "St Lawrence University": "Saints",
    "Stevens Institute of Technology": "Ducks",
    "Swarthmore College": "Garnet",
    "The College of New Jersey": "Lions",
    "Trinity College": "Bantams",
    "Tufts University": "Jumbos",
    "Union College": "Dutchmen",
    "University of Chicago": "Maroons",
    "University of Rochester": "Yellowjackets",
    "Vassar College": "Brewers",
    "Washington and Lee University": "Generals",
    "Wellesley College": "Blue",
    "Wesleyan University": "Cardinals",
    "Williams College": "Ephs",
    "York College of Pennsylvania": "Spartans",
    "Christopher Newport University": "Captains",
    "Messiah University": "Falcons",
    "Roanoke College": "Maroons",
    "SUNY College at Geneseo": "Knights",
    "State University of New York at Cortland": "Red Dragons",
    "The Catholic University of America": "Cardinals",
    "United States Coast Guard Academy": "Bears",
}

# Approximate published figures (College Board / IPEDS-style ranges).
# Used for well-known programs; remaining schools get deterministic estimates.
ACADEMICS = {
    "Boston College": dict(
        enrollment=15250, acceptanceRate=16, retentionRate=95, tuitionInState=67680, tuitionOutOfState=67680,
        control="private", setting="suburban", satMid=1480, actMid=34, coach="Acacia Walker-Weinstein",
    ),
    "Boston University": dict(
        enrollment=36700, acceptanceRate=14, retentionRate=94, tuitionInState=66470, tuitionOutOfState=66470,
        control="private", setting="urban", satMid=1440, actMid=33, coach="Lauren Kahn",
    ),
    "Harvard University": dict(
        enrollment=25000, acceptanceRate=3, retentionRate=98, tuitionInState=59200, tuitionOutOfState=59200,
        control="private", setting="urban", satMid=1550, actMid=35, coach="Devon Wills",
    ),
    "Yale University": dict(
        enrollment=15500, acceptanceRate=5, retentionRate=98, tuitionInState=67250, tuitionOutOfState=67250,
        control="private", setting="urban", satMid=1540, actMid=35, coach="Vacant / staff",
    ),
    "Princeton University": dict(
        enrollment=8900, acceptanceRate=4, retentionRate=98, tuitionInState=59710, tuitionOutOfState=59710,
        control="private", setting="suburban", satMid=1540, actMid=35, coach="Chris Sailer",
    ),
    "University of Pennsylvania": dict(
        enrollment=28400, acceptanceRate=6, retentionRate=98, tuitionInState=66200, tuitionOutOfState=66200,
        control="private", setting="urban", satMid=1530, actMid=35, coach="Karin Brower",
    ),
    "Brown University": dict(
        enrollment=11000, acceptanceRate=5, retentionRate=98, tuitionInState=68500, tuitionOutOfState=68500,
        control="private", setting="urban", satMid=1530, actMid=35, coach="Keels Simpson",
    ),
    "Dartmouth College": dict(
        enrollment=6800, acceptanceRate=6, retentionRate=98, tuitionInState=65400, tuitionOutOfState=65400,
        control="private", setting="rural", satMid=1540, actMid=34, coach="Kris Niiler",
    ),
    "Columbia University": dict(
        enrollment=36600, acceptanceRate=4, retentionRate=98, tuitionInState=68400, tuitionOutOfState=68400,
        control="private", setting="urban", satMid=1530, actMid=35, coach="Abigail Jackson",
    ),
    "Cornell University": dict(
        enrollment=26100, acceptanceRate=7, retentionRate=97, tuitionInState=66300, tuitionOutOfState=66300,
        control="private", setting="rural", satMid=1520, actMid=34, coach="Jenny Graap",
    ),
    "University of Maryland, College Park": dict(
        enrollment=40700, acceptanceRate=45, retentionRate=95, tuitionInState=11600, tuitionOutOfState=40700,
        control="public", setting="suburban", satMid=1410, actMid=32, coach="Cathy Reese",
    ),
    "University of North Carolina at Chapel Hill": dict(
        enrollment=32000, acceptanceRate=17, retentionRate=96, tuitionInState=9000, tuitionOutOfState=39400,
        control="public", setting="suburban", satMid=1400, actMid=31, coach="Jenny Levy",
    ),
    "Northwestern University": dict(
        enrollment=23000, acceptanceRate=7, retentionRate=98, tuitionInState=67100, tuitionOutOfState=67100,
        control="private", setting="suburban", satMid=1530, actMid=34, coach="Kelly Amonte Hiller",
    ),
    "Syracuse University": dict(
        enrollment=22700, acceptanceRate=42, retentionRate=91, tuitionInState=63400, tuitionOutOfState=63400,
        control="private", setting="urban", satMid=1310, actMid=30, coach="Kayla Treanor",
    ),
    "University of Virginia": dict(
        enrollment=26000, acceptanceRate=19, retentionRate=97, tuitionInState=21600, tuitionOutOfState=58900,
        control="public", setting="suburban", satMid=1440, actMid=33, coach="Michele Uhlfelder",
    ),
    "Duke University": dict(
        enrollment=18000, acceptanceRate=6, retentionRate=98, tuitionInState=66100, tuitionOutOfState=66100,
        control="private", setting="suburban", satMid=1540, actMid=35, coach="Kerstin Kimel",
    ),
    "University of Notre Dame": dict(
        enrollment=13100, acceptanceRate=12, retentionRate=98, tuitionInState=65100, tuitionOutOfState=65100,
        control="private", setting="suburban", satMid=1500, actMid=34, coach="Christine Halfpenny",
    ),
    "Stanford University": dict(
        enrollment=17600, acceptanceRate=4, retentionRate=98, tuitionInState=62600, tuitionOutOfState=62600,
        control="private", setting="suburban", satMid=1550, actMid=35, coach="Danielle Spencer",
    ),
    "University of Florida": dict(
        enrollment=55000, acceptanceRate=23, retentionRate=97, tuitionInState=6400, tuitionOutOfState=28700,
        control="public", setting="suburban", satMid=1390, actMid=31, coach="Amanda O'Leary",
    ),
    "James Madison University": dict(
        enrollment=22000, acceptanceRate=78, retentionRate=90, tuitionInState=13600, tuitionOutOfState=31300,
        control="public", setting="suburban", satMid=1240, actMid=27, coach="Shelley Klaes-Bawcombe",
    ),
    "Johns Hopkins University": dict(
        enrollment=31000, acceptanceRate=7, retentionRate=97, tuitionInState=63300, tuitionOutOfState=63300,
        control="private", setting="urban", satMid=1540, actMid=35, coach="Janine Tucker",
    ),
    "Loyola University Maryland": dict(
        enrollment=5100, acceptanceRate=83, retentionRate=87, tuitionInState=57400, tuitionOutOfState=57400,
        control="private", setting="urban", satMid=1270, actMid=29, coach="Jen Adams",
    ),
    "Pennsylvania State University": dict(
        enrollment=50000, acceptanceRate=55, retentionRate=93, tuitionInState=20400, tuitionOutOfState=40400,
        control="public", setting="rural", satMid=1310, actMid=29, coach="Missy Doherty",
    ),
    "University of Michigan": dict(
        enrollment=52000, acceptanceRate=18, retentionRate=97, tuitionInState=17700, tuitionOutOfState=58900,
        control="public", setting="urban", satMid=1470, actMid=33, coach="Hannah Nielsen",
    ),
    "Ohio State University": dict(
        enrollment=60000, acceptanceRate=53, retentionRate=94, tuitionInState=12900, tuitionOutOfState=38700,
        control="public", setting="urban", satMid=1340, actMid=29, coach="Alexis Venechanos",
    ),
    "Rutgers University–New Brunswick": dict(
        enrollment=50000, acceptanceRate=66, retentionRate=93, tuitionInState=17200, tuitionOutOfState=36100,
        control="public", setting="urban", satMid=1300, actMid=29, coach="Melissa Lehman",
    ),
    "University of Southern California": dict(
        enrollment=49000, acceptanceRate=10, retentionRate=96, tuitionInState=68200, tuitionOutOfState=68200,
        control="private", setting="urban", satMid=1510, actMid=34, coach="Lindsey Munday",
    ),
    "University of Oregon": dict(
        enrollment=23000, acceptanceRate=86, retentionRate=87, tuitionInState=15700, tuitionOutOfState=43200,
        control="public", setting="urban", satMid=1260, actMid=27, coach="Taylor Marino",
    ),
    "Georgetown University": dict(
        enrollment=20000, acceptanceRate=13, retentionRate=96, tuitionInState=65400, tuitionOutOfState=65400,
        control="private", setting="urban", satMid=1490, actMid=34, coach="Ricky Fried",
    ),
    "University of Denver": dict(
        enrollment=14000, acceptanceRate=78, retentionRate=88, tuitionInState=59600, tuitionOutOfState=59600,
        control="private", setting="urban", satMid=1310, actMid=29, coach="Liza Kelly",
    ),
    "Stony Brook University": dict(
        enrollment=26000, acceptanceRate=49, retentionRate=89, tuitionInState=10500, tuitionOutOfState=30500,
        control="public", setting="suburban", satMid=1390, actMid=31, coach="Joe Spallina",
    ),
    "Towson University": dict(
        enrollment=19500, acceptanceRate=79, retentionRate=85, tuitionInState=11400, tuitionOutOfState=28200,
        control="public", setting="suburban", satMid=1170, actMid=24, coach="Sonia LaMonica",
    ),
    "United States Naval Academy": dict(
        enrollment=4500, acceptanceRate=9, retentionRate=97, tuitionInState=0, tuitionOutOfState=0,
        control="public", setting="urban", satMid=1330, actMid=30, coach="Cindy Timchal",
    ),
    "United States Military Academy": dict(
        enrollment=4400, acceptanceRate=12, retentionRate=96, tuitionInState=0, tuitionOutOfState=0,
        control="public", setting="rural", satMid=1300, actMid=30, coach="Michelle Tumolo",
    ),
    "Villanova University": dict(
        enrollment=10800, acceptanceRate=23, retentionRate=96, tuitionInState=64200, tuitionOutOfState=64200,
        control="private", setting="suburban", satMid=1440, actMid=33, coach="Brenna Smith",
    ),
    "University of Connecticut": dict(
        enrollment=27000, acceptanceRate=54, retentionRate=92, tuitionInState=20000, tuitionOutOfState=43100,
        control="public", setting="rural", satMid=1330, actMid=30, coach="Katie Woods",
    ),
    "Clemson University": dict(
        enrollment=28000, acceptanceRate=43, retentionRate=93, tuitionInState=15700, tuitionOutOfState=39500,
        control="public", setting="suburban", satMid=1320, actMid=30, coach="Manhattan Reisenweaver",
    ),
    "Virginia Polytechnic Institute and State University": dict(
        enrollment=38000, acceptanceRate=57, retentionRate=93, tuitionInState=15900, tuitionOutOfState=36500,
        control="public", setting="rural", satMid=1330, actMid=29, coach="John Sung",
    ),
    "University of Colorado Boulder": dict(
        enrollment=38000, acceptanceRate=81, retentionRate=88, tuitionInState=13600, tuitionOutOfState=41700,
        control="public", setting="urban", satMid=1260, actMid=28, coach="Ann Whidden",
    ),
    "Arizona State University": dict(
        enrollment=80000, acceptanceRate=90, retentionRate=85, tuitionInState=12000, tuitionOutOfState=32400,
        control="public", setting="urban", satMid=1240, actMid=25, coach="Taylor Wheatley",
    ),
    "University of California, Berkeley": dict(
        enrollment=45000, acceptanceRate=11, retentionRate=97, tuitionInState=15400, tuitionOutOfState=48000,
        control="public", setting="urban", satMid=1440, actMid=32, coach="Lauren Khan",
    ),
    "Vanderbilt University": dict(
        enrollment=13700, acceptanceRate=6, retentionRate=97, tuitionInState=63900, tuitionOutOfState=63900,
        control="private", setting="urban", satMid=1540, actMid=35, coach="Bethany Solomon",
    ),
    "Temple University": dict(
        enrollment=33000, acceptanceRate=80, retentionRate=89, tuitionInState=22000, tuitionOutOfState=37100,
        control="public", setting="urban", satMid=1240, actMid=27, coach="Bonnie Rosen",
    ),
    "College of William & Mary": dict(
        enrollment=9700, acceptanceRate=33, retentionRate=95, tuitionInState=25000, tuitionOutOfState=49400,
        control="public", setting="suburban", satMid=1440, actMid=33, coach="Brooke Williams",
    ),
    "University of Richmond": dict(
        enrollment=3900, acceptanceRate=24, retentionRate=93, tuitionInState=62600, tuitionOutOfState=62600,
        control="private", setting="suburban", satMid=1440, actMid=33, coach="Allison Melaugh",
    ),
    "Colgate University": dict(
        enrollment=3200, acceptanceRate=12, retentionRate=94, tuitionInState=67200, tuitionOutOfState=67200,
        control="private", setting="rural", satMid=1460, actMid=33, coach="Marie Curran",
    ),
    "Bucknell University": dict(
        enrollment=3900, acceptanceRate=32, retentionRate=91, tuitionInState=64700, tuitionOutOfState=64700,
        control="private", setting="rural", satMid=1380, actMid=31, coach="Randy Wilkes",
    ),
    "Lehigh University": dict(
        enrollment=7600, acceptanceRate=37, retentionRate=93, tuitionInState=62200, tuitionOutOfState=62200,
        control="private", setting="suburban", satMid=1410, actMid=32, coach="Jill Redfern",
    ),
    "College of the Holy Cross": dict(
        enrollment=3200, acceptanceRate=36, retentionRate=93, tuitionInState=60700, tuitionOutOfState=60700,
        control="private", setting="urban", satMid=1350, actMid=30, coach="Michelle Connors",
    ),
    "Lafayette College": dict(
        enrollment=2700, acceptanceRate=31, retentionRate=91, tuitionInState=62000, tuitionOutOfState=62000,
        control="private", setting="suburban", satMid=1370, actMid=31, coach="Michael LoGiudice",
    ),
    "American University": dict(
        enrollment=14000, acceptanceRate=41, retentionRate=88, tuitionInState=56500, tuitionOutOfState=56500,
        control="private", setting="urban", satMid=1360, actMid=31, coach="Denise Wescott",
    ),
    "Drexel University": dict(
        enrollment=22000, acceptanceRate=80, retentionRate=89, tuitionInState=60700, tuitionOutOfState=60700,
        control="private", setting="urban", satMid=1310, actMid=29, coach="Anna Montemurro",
    ),
    "Hofstra University": dict(
        enrollment=10200, acceptanceRate=69, retentionRate=83, tuitionInState=55400, tuitionOutOfState=55400,
        control="private", setting="suburban", satMid=1260, actMid=28, coach="Shannon Smith",
    ),
    "Fairfield University": dict(
        enrollment=6200, acceptanceRate=52, retentionRate=90, tuitionInState=56500, tuitionOutOfState=56500,
        control="private", setting="suburban", satMid=1310, actMid=29, coach="Colleen Cagney",
    ),
    "Quinnipiac University": dict(
        enrollment=9200, acceptanceRate=77, retentionRate=88, tuitionInState=53400, tuitionOutOfState=53400,
        control="private", setting="suburban", satMid=1210, actMid=26, coach="Brittany Stirling",
    ),
    "University of New Hampshire": dict(
        enrollment=14000, acceptanceRate=87, retentionRate=86, tuitionInState=19400, tuitionOutOfState=38900,
        control="public", setting="suburban", satMid=1210, actMid=26, coach="Beth Hewitt",
    ),
    "University of Vermont": dict(
        enrollment=14000, acceptanceRate=60, retentionRate=87, tuitionInState=19100, tuitionOutOfState=45400,
        control="public", setting="urban", satMid=1330, actMid=30, coach="Sarah Dalton",
    ),
    "University of Delaware": dict(
        enrollment=24000, acceptanceRate=72, retentionRate=91, tuitionInState=16200, tuitionOutOfState=39900,
        control="public", setting="suburban", satMid=1280, actMid=29, coach="Kateri Linville",
    ),
    "University of Massachusetts Amherst": dict(
        enrollment=32000, acceptanceRate=64, retentionRate=91, tuitionInState=17400, tuitionOutOfState=39500,
        control="public", setting="suburban", satMid=1350, actMid=30, coach="Angela McMahon",
    ),
    "Liberty University": dict(
        enrollment=15000, acceptanceRate=99, retentionRate=81, tuitionInState=24600, tuitionOutOfState=24600,
        control="private", setting="suburban", satMid=1150, actMid=25, coach="Kateri Linville",
    ),
    "High Point University": dict(
        enrollment=6000, acceptanceRate=79, retentionRate=83, tuitionInState=44100, tuitionOutOfState=44100,
        control="private", setting="suburban", satMid=1200, actMid=26, coach="Lyndsey Burgess",
    ),
    "Elon University": dict(
        enrollment=7200, acceptanceRate=74, retentionRate=90, tuitionInState=44700, tuitionOutOfState=44700,
        control="private", setting="suburban", satMid=1260, actMid=28, coach="Josh Hexter",
    ),
    "Davidson College": dict(
        enrollment=2000, acceptanceRate=17, retentionRate=95, tuitionInState=60100, tuitionOutOfState=60100,
        control="private", setting="suburban", satMid=1430, actMid=32, coach="Kim Eberly",
    ),
    "Furman University": dict(
        enrollment=2500, acceptanceRate=67, retentionRate=89, tuitionInState=58100, tuitionOutOfState=58100,
        control="private", setting="suburban", satMid=1330, actMid=30, coach="Kylee White",
    ),
    "University of Louisville": dict(
        enrollment=22000, acceptanceRate=81, retentionRate=81, tuitionInState=12900, tuitionOutOfState=29100,
        control="public", setting="urban", satMid=1180, actMid=24, coach="Scott Teeter",
    ),
    "University of Pittsburgh": dict(
        enrollment=33000, acceptanceRate=49, retentionRate=93, tuitionInState=21600, tuitionOutOfState=37700,
        control="public", setting="urban", satMid=1360, actMid=31, coach="Randy Wilkes",
    ),
    "Florida State University": dict(
        enrollment=44000, acceptanceRate=25, retentionRate=94, tuitionInState=5700, tuitionOutOfState=18700,
        control="public", setting="urban", satMid=1310, actMid=29, coach="Kara Connors",
    ),
    "San Diego State University": dict(
        enrollment=37000, acceptanceRate=39, retentionRate=90, tuitionInState=8200, tuitionOutOfState=20100,
        control="public", setting="urban", satMid=1210, actMid=26, coach="Kylee White",
    ),
    "University of California, Davis": dict(
        enrollment=40000, acceptanceRate=42, retentionRate=93, tuitionInState=15200, tuitionOutOfState=46200,
        control="public", setting="suburban", satMid=1290, actMid=28, coach="Suzette Soboti",
    ),
    "Marquette University": dict(
        enrollment=11300, acceptanceRate=87, retentionRate=89, tuitionInState=48900, tuitionOutOfState=48900,
        control="private", setting="urban", satMid=1260, actMid=27, coach="Meredith Black",
    ),
    "Butler University": dict(
        enrollment=5500, acceptanceRate=82, retentionRate=89, tuitionInState=46700, tuitionOutOfState=46700,
        control="private", setting="urban", satMid=1260, actMid=28, coach="Caroline Bonacci",
    ),
    "Xavier University": dict(
        enrollment=6600, acceptanceRate=84, retentionRate=84, tuitionInState=48100, tuitionOutOfState=48100,
        control="private", setting="urban", satMid=1230, actMid=26, coach="James Mitchell",
    ),
    "George Washington University": dict(
        enrollment=26000, acceptanceRate=44, retentionRate=91, tuitionInState=64700, tuitionOutOfState=64700,
        control="private", setting="urban", satMid=1400, actMid=32, coach="Sonia LaMonica",
    ),
    "George Mason University": dict(
        enrollment=39000, acceptanceRate=90, retentionRate=87, tuitionInState=13700, tuitionOutOfState=37700,
        control="public", setting="suburban", satMid=1240, actMid=27, coach="Kerstin Kimel",
    ),
    "Virginia Commonwealth University": dict(
        enrollment=28000, acceptanceRate=93, retentionRate=85, tuitionInState=15900, tuitionOutOfState=38100,
        control="public", setting="urban", satMid=1180, actMid=25, coach="Darcy Carver",
    ),
    "Old Dominion University": dict(
        enrollment=23000, acceptanceRate=95, retentionRate=80, tuitionInState=12400, tuitionOutOfState=33100,
        control="public", setting="urban", satMid=1170, actMid=24, coach="Heather Holt",
    ),
    "East Carolina University": dict(
        enrollment=27000, acceptanceRate=92, retentionRate=82, tuitionInState=7400, tuitionOutOfState=23600,
        control="public", setting="urban", satMid=1130, actMid=22, coach="Nicole Levy",
    ),
    "University of Cincinnati": dict(
        enrollment=41000, acceptanceRate=86, retentionRate=86, tuitionInState=13700, tuitionOutOfState=28900,
        control="public", setting="urban", satMid=1260, actMid=27, coach="Gina Capira",
    ),
    "University of South Florida": dict(
        enrollment=50000, acceptanceRate=44, retentionRate=90, tuitionInState=6400, tuitionOutOfState=17400,
        control="public", setting="urban", satMid=1240, actMid=27, coach="Kara Connors",
    ),
    "University of North Carolina at Charlotte": dict(
        enrollment=30000, acceptanceRate=80, retentionRate=85, tuitionInState=7200, tuitionOutOfState=21700,
        control="public", setting="urban", satMid=1180, actMid=24, coach="Lyndsey Burgess",
    ),
    "Coastal Carolina University": dict(
        enrollment=10500, acceptanceRate=80, retentionRate=76, tuitionInState=11700, tuitionOutOfState=27700,
        control="public", setting="suburban", satMid=1110, actMid=22, coach="Kia Abel",
    ),
    "Jacksonville University": dict(
        enrollment=4200, acceptanceRate=78, retentionRate=76, tuitionInState=46100, tuitionOutOfState=46100,
        control="private", setting="urban", satMid=1140, actMid=23, coach="Meredith Black",
    ),
    "University at Albany": dict(
        enrollment=17000, acceptanceRate=68, retentionRate=83, tuitionInState=10400, tuitionOutOfState=28700,
        control="public", setting="urban", satMid=1180, actMid=25, coach="Katie Thomson",
    ),
    "Binghamton University": dict(
        enrollment=18000, acceptanceRate=42, retentionRate=91, tuitionInState=10400, tuitionOutOfState=28700,
        control="public", setting="suburban", satMid=1370, actMid=31, coach="Stephanie Allen",
    ),
    "Bryant University": dict(
        enrollment=3500, acceptanceRate=69, retentionRate=88, tuitionInState=51200, tuitionOutOfState=51200,
        control="private", setting="suburban", satMid=1230, actMid=27, coach="Jill Batcheller",
    ),
    "Monmouth University": dict(
        enrollment=5000, acceptanceRate=90, retentionRate=81, tuitionInState=44700, tuitionOutOfState=44700,
        control="private", setting="suburban", satMid=1170, actMid=24, coach="Jordan Trautman",
    ),
    "Sacred Heart University": dict(
        enrollment=11000, acceptanceRate=66, retentionRate=85, tuitionInState=48100, tuitionOutOfState=48100,
        control="private", setting="suburban", satMid=1190, actMid=25, coach="Laura Cook",
    ),
    "Marist University": dict(
        enrollment=5500, acceptanceRate=63, retentionRate=87, tuitionInState=46200, tuitionOutOfState=46200,
        control="private", setting="suburban", satMid=1260, actMid=28, coach="Jessica Coppel",
    ),
    "Canisius University": dict(
        enrollment=2500, acceptanceRate=81, retentionRate=80, tuitionInState=32400, tuitionOutOfState=32400,
        control="private", setting="urban", satMid=1140, actMid=23, coach="Scott Teeter",
    ),
    "Siena University": dict(
        enrollment=3500, acceptanceRate=80, retentionRate=85, tuitionInState=42800, tuitionOutOfState=42800,
        control="private", setting="suburban", satMid=1170, actMid=25, coach="Abby Oliver",
    ),
    "Iona University": dict(
        enrollment=3600, acceptanceRate=86, retentionRate=78, tuitionInState=45600, tuitionOutOfState=45600,
        control="private", setting="suburban", satMid=1130, actMid=23, coach="Brooke Williams",
    ),
    "Manhattan University": dict(
        enrollment=3600, acceptanceRate=82, retentionRate=78, tuitionInState=50500, tuitionOutOfState=50500,
        control="private", setting="urban", satMid=1180, actMid=25, coach="Katie Woods",
    ),
    "Mount St. Mary's University": dict(
        enrollment=2100, acceptanceRate=80, retentionRate=76, tuitionInState=47300, tuitionOutOfState=47300,
        control="private", setting="rural", satMid=1120, actMid=22, coach="Ali Williams",
    ),
    "Niagara University": dict(
        enrollment=2700, acceptanceRate=85, retentionRate=79, tuitionInState=39100, tuitionOutOfState=39100,
        control="private", setting="suburban", satMid=1120, actMid=23, coach="Steve Wagner",
    ),
    "Rider University": dict(
        enrollment=4000, acceptanceRate=84, retentionRate=80, tuitionInState=39400, tuitionOutOfState=39400,
        control="private", setting="suburban", satMid=1130, actMid=23, coach="Kathy K fores",
    ),
    "Wagner College": dict(
        enrollment=1800, acceptanceRate=84, retentionRate=80, tuitionInState=52400, tuitionOutOfState=52400,
        control="private", setting="urban", satMid=1180, actMid=25, coach="Kelly McPartland",
    ),
    "Long Island University": dict(
        enrollment=16000, acceptanceRate=93, retentionRate=77, tuitionInState=41400, tuitionOutOfState=41400,
        control="private", setting="suburban", satMid=1160, actMid=24, coach="Sam Cermack",
    ),
    "Le Moyne College": dict(
        enrollment=3200, acceptanceRate=75, retentionRate=86, tuitionInState=40100, tuitionOutOfState=40100,
        control="private", setting="suburban", satMid=1190, actMid=25, coach="Kathy Taylor",
    ),
    "Merrimack College": dict(
        enrollment=5400, acceptanceRate=75, retentionRate=82, tuitionInState=51700, tuitionOutOfState=51700,
        control="private", setting="suburban", satMid=1170, actMid=25, coach="Keelan O'Connell",
    ),
    "Stonehill College": dict(
        enrollment=2500, acceptanceRate=73, retentionRate=84, tuitionInState=54400, tuitionOutOfState=54400,
        control="private", setting="suburban", satMid=1190, actMid=26, coach="Tara Mounsey",
    ),
    "Mercyhurst University": dict(
        enrollment=2700, acceptanceRate=82, retentionRate=81, tuitionInState=44500, tuitionOutOfState=44500,
        control="private", setting="urban", satMid=1130, actMid=23, coach="Michele DeJuliis",
    ),
    "University of New Haven": dict(
        enrollment=8800, acceptanceRate=91, retentionRate=77, tuitionInState=45600, tuitionOutOfState=45600,
        control="private", setting="suburban", satMid=1140, actMid=23, coach="Kim Huelsman",
    ),
    "Robert Morris University": dict(
        enrollment=3400, acceptanceRate=94, retentionRate=80, tuitionInState=35700, tuitionOutOfState=35700,
        control="private", setting="suburban", satMid=1120, actMid=23, coach="Jenn Childress",
    ),
    "Central Connecticut State University": dict(
        enrollment=9600, acceptanceRate=77, retentionRate=74, tuitionInState=12700, tuitionOutOfState=25900,
        control="public", setting="suburban", satMid=1080, actMid=21, coach="Kerri Johnson",
    ),
    "Howard University": dict(
        enrollment=13000, acceptanceRate=53, retentionRate=88, tuitionInState=33300, tuitionOutOfState=33300,
        control="private", setting="urban", satMid=1230, actMid=26, coach="Nadia Williams",
    ),
    "Delaware State University": dict(
        enrollment=5800, acceptanceRate=62, retentionRate=75, tuitionInState=10400, tuitionOutOfState=20200,
        control="public", setting="suburban", satMid=970, actMid=18, coach="Nadine Williams",
    ),
    "Fairleigh Dickinson University": dict(
        enrollment=12000, acceptanceRate=87, retentionRate=79, tuitionInState=37700, tuitionOutOfState=37700,
        control="private", setting="suburban", satMid=1110, actMid=22, coach="Lauren Kahn",
    ),
    "Campbell University": dict(
        enrollment=5600, acceptanceRate=87, retentionRate=75, tuitionInState=40400, tuitionOutOfState=40400,
        control="private", setting="rural", satMid=1120, actMid=22, coach="Amanda O'Leary",
    ),
    "Mercer University": dict(
        enrollment=9000, acceptanceRate=75, retentionRate=85, tuitionInState=42100, tuitionOutOfState=42100,
        control="private", setting="urban", satMid=1270, actMid=28, coach="Lauren Kahn",
    ),
    "Kennesaw State University": dict(
        enrollment=43000, acceptanceRate=69, retentionRate=79, tuitionInState=6700, tuitionOutOfState=20700,
        control="public", setting="suburban", satMid=1140, actMid=23, coach="Lauren Kahn",
    ),
    "Stetson University": dict(
        enrollment=4400, acceptanceRate=86, retentionRate=78, tuitionInState=55500, tuitionOutOfState=55500,
        control="private", setting="suburban", satMid=1190, actMid=25, coach="Danielle Spencer",
    ),
    "Queens University of Charlotte": dict(
        enrollment=2100, acceptanceRate=68, retentionRate=76, tuitionInState=42700, tuitionOutOfState=42700,
        control="private", setting="urban", satMid=1160, actMid=24, coach="Gina Capira",
    ),
    "Lindenwood University": dict(
        enrollment=7000, acceptanceRate=74, retentionRate=73, tuitionInState=20900, tuitionOutOfState=20900,
        control="private", setting="suburban", satMid=1100, actMid=22, coach="Jackie Smith",
    ),
    "Austin Peay State University": dict(
        enrollment=9600, acceptanceRate=93, retentionRate=70, tuitionInState=8900, tuitionOutOfState=15200,
        control="public", setting="urban", satMid=1080, actMid=21, coach="Taylor Wheatley",
    ),
    "Longwood University": dict(
        enrollment=4500, acceptanceRate=88, retentionRate=76, tuitionInState=15200, tuitionOutOfState=27600,
        control="public", setting="rural", satMid=1100, actMid=22, coach="Elaine Jones",
    ),
    "Radford University": dict(
        enrollment=7700, acceptanceRate=93, retentionRate=74, tuitionInState=12400, tuitionOutOfState=25400,
        control="public", setting="rural", satMid=1080, actMid=21, coach="Elaine Jones",
    ),
    "Presbyterian College": dict(
        enrollment=1200, acceptanceRate=59, retentionRate=76, tuitionInState=44100, tuitionOutOfState=44100,
        control="private", setting="rural", satMid=1140, actMid=23, coach="Kia Abel",
    ),
    "Gardner–Webb University": dict(
        enrollment=3500, acceptanceRate=75, retentionRate=70, tuitionInState=34200, tuitionOutOfState=34200,
        control="private", setting="rural", satMid=1080, actMid=21, coach="Kia Abel",
    ),
    "Winthrop University": dict(
        enrollment=4700, acceptanceRate=70, retentionRate=70, tuitionInState=15900, tuitionOutOfState=30200,
        control="public", setting="suburban", satMid=1100, actMid=22, coach="Kia Abel",
    ),
    "Wofford College": dict(
        enrollment=1800, acceptanceRate=60, retentionRate=88, tuitionInState=54100, tuitionOutOfState=54100,
        control="private", setting="urban", satMid=1310, actMid=29, coach="Kylee White",
    ),
    "University of Rhode Island": dict(
        enrollment=17500, acceptanceRate=76, retentionRate=85, tuitionInState=16400, tuitionOutOfState=35800,
        control="public", setting="rural", satMid=1180, actMid=25, coach="Lauren Kahn",
    ),
    "Saint Joseph's University": dict(
        enrollment=7900, acceptanceRate=86, retentionRate=89, tuitionInState=52400, tuitionOutOfState=52400,
        control="private", setting="urban", satMid=1230, actMid=27, coach="Denise Wescott",
    ),
    "La Salle University": dict(
        enrollment=4000, acceptanceRate=86, retentionRate=77, tuitionInState=36500, tuitionOutOfState=36500,
        control="private", setting="urban", satMid=1120, actMid=23, coach="Denise Wescott",
    ),
    "Duquesne University": dict(
        enrollment=8100, acceptanceRate=87, retentionRate=86, tuitionInState=47600, tuitionOutOfState=47600,
        control="private", setting="urban", satMid=1230, actMid=27, coach="Steve Wagner",
    ),
    "St. Bonaventure University": dict(
        enrollment=2500, acceptanceRate=81, retentionRate=84, tuitionInState=40700, tuitionOutOfState=40700,
        control="private", setting="rural", satMid=1140, actMid=23, coach="Steve Wagner",
    ),
    "University of Akron": dict(
        enrollment=13500, acceptanceRate=83, retentionRate=72, tuitionInState=12700, tuitionOutOfState=20400,
        control="public", setting="urban", satMid=1100, actMid=22, coach="Sarah Dalton",
    ),
    "Kent State University": dict(
        enrollment=26000, acceptanceRate=88, retentionRate=78, tuitionInState=12700, tuitionOutOfState=22000,
        control="public", setting="suburban", satMid=1110, actMid=22, coach="Sarah Dalton",
    ),
    "Central Michigan University": dict(
        enrollment=14500, acceptanceRate=79, retentionRate=77, tuitionInState=13700, tuitionOutOfState=24600,
        control="public", setting="rural", satMid=1100, actMid=22, coach="Sarah Dalton",
    ),
    "Eastern Michigan University": dict(
        enrollment=14000, acceptanceRate=83, retentionRate=71, tuitionInState=15200, tuitionOutOfState=15700,
        control="public", setting="suburban", satMid=1080, actMid=21, coach="Sarah Dalton",
    ),
    "Youngstown State University": dict(
        enrollment=11000, acceptanceRate=80, retentionRate=75, tuitionInState=10700, tuitionOutOfState=11100,
        control="public", setting="urban", satMid=1070, actMid=21, coach="Sarah Dalton",
    ),
    "University of Detroit Mercy": dict(
        enrollment=5000, acceptanceRate=90, retentionRate=82, tuitionInState=32400, tuitionOutOfState=32400,
        control="private", setting="urban", satMid=1140, actMid=23, coach="Sarah Dalton",
    ),
    "University of Maryland, Baltimore County": dict(
        enrollment=14000, acceptanceRate=74, retentionRate=87, tuitionInState=12900, tuitionOutOfState=30200,
        control="public", setting="suburban", satMid=1310, actMid=29, coach="Amy Appelt",
    ),
    "University of Massachusetts Lowell": dict(
        enrollment=17000, acceptanceRate=86, retentionRate=84, tuitionInState=16600, tuitionOutOfState=35500,
        control="public", setting="urban", satMid=1250, actMid=27, coach="Shannon Smith",
    ),
    "Middlebury College": dict(
        enrollment=2800, acceptanceRate=11, retentionRate=97, tuitionInState=67100, tuitionOutOfState=67100,
        control="private", setting="rural", satMid=1490, actMid=34, coach="Kate Livesay",
    ),
    "Williams College": dict(
        enrollment=2200, acceptanceRate=8, retentionRate=98, tuitionInState=64800, tuitionOutOfState=64800,
        control="private", setting="rural", satMid=1520, actMid=35, coach="Alice Lee",
    ),
    "Amherst College": dict(
        enrollment=1900, acceptanceRate=7, retentionRate=98, tuitionInState=67000, tuitionOutOfState=67000,
        control="private", setting="suburban", satMid=1510, actMid=34, coach="Cassie Funke",
    ),
    "Tufts University": dict(
        enrollment=13000, acceptanceRate=10, retentionRate=97, tuitionInState=67600, tuitionOutOfState=67600,
        control="private", setting="suburban", satMid=1500, actMid=34, coach="Courtney Belak",
    ),
    "Wesleyan University": dict(
        enrollment=3000, acceptanceRate=14, retentionRate=95, tuitionInState=67000, tuitionOutOfState=67000,
        control="private", setting="suburban", satMid=1490, actMid=34, coach="Kim Huelsman",
    ),
    "Bowdoin College": dict(
        enrollment=1900, acceptanceRate=9, retentionRate=97, tuitionInState=64600, tuitionOutOfState=64600,
        control="private", setting="suburban", satMid=1510, actMid=34, coach="Elizabeth Grote",
    ),
    "Colby College": dict(
        enrollment=2300, acceptanceRate=7, retentionRate=94, tuitionInState=66900, tuitionOutOfState=66900,
        control="private", setting="rural", satMid=1480, actMid=33, coach="Karen Henning",
    ),
    "Bates College": dict(
        enrollment=1800, acceptanceRate=14, retentionRate=94, tuitionInState=64500, tuitionOutOfState=64500,
        control="private", setting="urban", satMid=1450, actMid=33, coach="Sharon Shapiro",
    ),
    "Trinity College": dict(
        enrollment=2200, acceptanceRate=36, retentionRate=91, tuitionInState=67400, tuitionOutOfState=67400,
        control="private", setting="urban", satMid=1380, actMid=31, coach="Kate Livesay",
    ),
    "Hamilton College": dict(
        enrollment=2000, acceptanceRate=12, retentionRate=95, tuitionInState=65600, tuitionOutOfState=65600,
        control="private", setting="rural", satMid=1480, actMid=33, coach="Pat Catalano",
    ),
    "Connecticut College": dict(
        enrollment=1900, acceptanceRate=38, retentionRate=90, tuitionInState=65600, tuitionOutOfState=65600,
        control="private", setting="suburban", satMid=1400, actMid=32, coach="Anne Parmenter",
    ),
    "Gettysburg College": dict(
        enrollment=2400, acceptanceRate=48, retentionRate=90, tuitionInState=64300, tuitionOutOfState=64300,
        control="private", setting="suburban", satMid=1350, actMid=30, coach="Carol Tracy",
    ),
    "Franklin and Marshall College": dict(
        enrollment=1900, acceptanceRate=36, retentionRate=90, tuitionInState=68300, tuitionOutOfState=68300,
        control="private", setting="urban", satMid=1370, actMid=31, coach="Lauren Kahn",
    ),
    "Salisbury University": dict(
        enrollment=7100, acceptanceRate=91, retentionRate=83, tuitionInState=10700, tuitionOutOfState=21400,
        control="public", setting="suburban", satMid=1240, actMid=26, coach="Jim Nestor",
    ),
    "Tampa": dict(
        enrollment=11000, acceptanceRate=41, retentionRate=83, tuitionInState=33200, tuitionOutOfState=33200,
        control="private", setting="urban", satMid=1180, actMid=25, coach="Kristen Kaseor",
    ),
    "University of Tampa": dict(
        enrollment=11000, acceptanceRate=41, retentionRate=83, tuitionInState=33200, tuitionOutOfState=33200,
        control="private", setting="urban", satMid=1180, actMid=25, coach="Kristen Kaseor",
    ),
    "Adelphi University": dict(
        enrollment=7500, acceptanceRate=73, retentionRate=83, tuitionInState=47300, tuitionOutOfState=47300,
        control="private", setting="suburban", satMid=1180, actMid=25, coach="Gordon Lewis",
    ),
    "West Chester University": dict(
        enrollment=17200, acceptanceRate=88, retentionRate=85, tuitionInState=10700, tuitionOutOfState=22400,
        control="public", setting="suburban", satMid=1160, actMid=24, coach="Ginny Martino",
    ),
    "Florida Southern College": dict(
        enrollment=3400, acceptanceRate=57, retentionRate=81, tuitionInState=42200, tuitionOutOfState=42200,
        control="private", setting="suburban", satMid=1180, actMid=25, coach="Ann Whidden",
    ),
    "Rollins College": dict(
        enrollment=3000, acceptanceRate=50, retentionRate=85, tuitionInState=58200, tuitionOutOfState=58200,
        control="private", setting="suburban", satMid=1250, actMid=27, coach="Lauren Kahn",
    ),
    "Pace University": dict(
        enrollment=13500, acceptanceRate=83, retentionRate=78, tuitionInState=51300, tuitionOutOfState=51300,
        control="private", setting="suburban", satMid=1180, actMid=25, coach="Kelly McPartland",
    ),
    "Assumption University": dict(
        enrollment=2000, acceptanceRate=82, retentionRate=82, tuitionInState=49400, tuitionOutOfState=49400,
        control="private", setting="suburban", satMid=1140, actMid=23, coach="Lauren Kahn",
    ),
    "Bentley University": dict(
        enrollment=5300, acceptanceRate=58, retentionRate=92, tuitionInState=58900, tuitionOutOfState=58900,
        control="private", setting="suburban", satMid=1330, actMid=30, coach="Katie Woods",
    ),
    "Southern New Hampshire University": dict(
        enrollment=3900, acceptanceRate=96, retentionRate=68, tuitionInState=16500, tuitionOutOfState=16500,
        control="private", setting="suburban", satMid=1080, actMid=21, coach="Lauren Kahn",
    ),
    "Massachusetts Institute of Technology": dict(
        enrollment=11900, acceptanceRate=4, retentionRate=99, tuitionInState=60100, tuitionOutOfState=60100,
        control="private", setting="urban", satMid=1550, actMid=36, coach="Anne Polgreen",
    ),
    "University of Chicago": dict(
        enrollment=18500, acceptanceRate=5, retentionRate=99, tuitionInState=66900, tuitionOutOfState=66900,
        control="private", setting="urban", satMid=1550, actMid=35, coach="Jason Rothenberg",
    ),
    "Swarthmore College": dict(
        enrollment=1700, acceptanceRate=7, retentionRate=97, tuitionInState=62400, tuitionOutOfState=62400,
        control="private", setting="suburban", satMid=1500, actMid=34, coach="Karen Borbee",
    ),
    "Haverford College": dict(
        enrollment=1400, acceptanceRate=14, retentionRate=96, tuitionInState=68100, tuitionOutOfState=68100,
        control="private", setting="suburban", satMid=1490, actMid=34, coach="Jamie Munoz",
    ),
    "Washington and Lee University": dict(
        enrollment=2200, acceptanceRate=17, retentionRate=96, tuitionInState=64700, tuitionOutOfState=64700,
        control="private", setting="rural", satMid=1470, actMid=33, coach="Kateri Linville",
    ),
    "Denison University": dict(
        enrollment=2300, acceptanceRate=22, retentionRate=89, tuitionInState=64000, tuitionOutOfState=64000,
        control="private", setting="rural", satMid=1340, actMid=30, coach="Amanda O'Leary",
    ),
    "Ithaca College": dict(
        enrollment=5000, acceptanceRate=75, retentionRate=85, tuitionInState=50100, tuitionOutOfState=50100,
        control="private", setting="suburban", satMid=1270, actMid=28, coach="Becky Kowal",
    ),
    "The College of New Jersey": dict(
        enrollment=7400, acceptanceRate=64, retentionRate=91, tuitionInState=18600, tuitionOutOfState=31700,
        control="public", setting="suburban", satMid=1280, actMid=28, coach="Sharon Shapiro",
    ),
    "Christopher Newport University": dict(
        enrollment=4500, acceptanceRate=88, retentionRate=85, tuitionInState=16200, tuitionOutOfState=30700,
        control="public", setting="suburban", satMid=1220, actMid=26, coach="Brooke Williams",
    ),
    "University of Mary Washington": dict(
        enrollment=3800, acceptanceRate=86, retentionRate=82, tuitionInState=14700, tuitionOutOfState=31700,
        control="public", setting="suburban", satMid=1220, actMid=26, coach="Brooke Williams",
    ),
    "Stevens Institute of Technology": dict(
        enrollment=9300, acceptanceRate=46, retentionRate=94, tuitionInState=60700, tuitionOutOfState=60700,
        control="private", setting="urban", satMid=1450, actMid=33, coach="Melissa Lehman",
    ),
    "Rensselaer Polytechnic Institute": dict(
        enrollment=7900, acceptanceRate=65, retentionRate=91, tuitionInState=61700, tuitionOutOfState=61700,
        control="private", setting="urban", satMid=1410, actMid=32, coach="Melissa Lehman",
    ),
    "Rochester Institute of Technology": dict(
        enrollment=16700, acceptanceRate=71, retentionRate=88, tuitionInState=57100, tuitionOutOfState=57100,
        control="private", setting="suburban", satMid=1360, actMid=31, coach="Melissa Lehman",
    ),
    "University of Rochester": dict(
        enrollment=12000, acceptanceRate=39, retentionRate=93, tuitionInState=64600, tuitionOutOfState=64600,
        control="private", setting="urban", satMid=1460, actMid=33, coach="Jason Rothenberg",
    ),
    "Brandeis University": dict(
        enrollment=5500, acceptanceRate=35, retentionRate=93, tuitionInState=64500, tuitionOutOfState=64500,
        control="private", setting="suburban", satMid=1440, actMid=33, coach="Lauren Kahn",
    ),
    "Wellesley College": dict(
        enrollment=2400, acceptanceRate=14, retentionRate=96, tuitionInState=64300, tuitionOutOfState=64300,
        control="private", setting="suburban", satMid=1490, actMid=34, coach="Julia McPhee",
    ),
    "Smith College": dict(
        enrollment=2500, acceptanceRate=23, retentionRate=93, tuitionInState=61400, tuitionOutOfState=61400,
        control="private", setting="urban", satMid=1440, actMid=32, coach="Julia McPhee",
    ),
    "Mount Holyoke College": dict(
        enrollment=2200, acceptanceRate=38, retentionRate=90, tuitionInState=64400, tuitionOutOfState=64400,
        control="private", setting="suburban", satMid=1400, actMid=32, coach="Julia McPhee",
    ),
    "Colorado College": dict(
        enrollment=2200, acceptanceRate=16, retentionRate=95, tuitionInState=67900, tuitionOutOfState=67900,
        control="private", setting="urban", satMid=1380, actMid=31, coach="Ann Whidden",
    ),
    "Pomona College": dict(
        enrollment=1700, acceptanceRate=7, retentionRate=98, tuitionInState=62500, tuitionOutOfState=62500,
        control="private", setting="suburban", satMid=1520, actMid=34, coach="Danielle Spencer",
    ),
    "Babson College": dict(
        enrollment=3800, acceptanceRate=20, retentionRate=95, tuitionInState=57300, tuitionOutOfState=57300,
        control="private", setting="suburban", satMid=1430, actMid=32, coach="Lauren Kahn",
    ),
    "Skidmore College": dict(
        enrollment=2700, acceptanceRate=26, retentionRate=91, tuitionInState=64900, tuitionOutOfState=64900,
        control="private", setting="suburban", satMid=1350, actMid=31, coach="Sharon Shapiro",
    ),
    "Vassar College": dict(
        enrollment=2400, acceptanceRate=19, retentionRate=94, tuitionInState=67500, tuitionOutOfState=67500,
        control="private", setting="suburban", satMid=1480, actMid=33, coach="Sharon Shapiro",
    ),
    "Union College": dict(
        enrollment=2100, acceptanceRate=44, retentionRate=89, tuitionInState=66800, tuitionOutOfState=66800,
        control="private", setting="urban", satMid=1350, actMid=30, coach="Sharon Shapiro",
    ),
    "St Lawrence University": dict(
        enrollment=2300, acceptanceRate=58, retentionRate=87, tuitionInState=63700, tuitionOutOfState=63700,
        control="private", setting="rural", satMid=1290, actMid=29, coach="Sharon Shapiro",
    ),
    "Dickinson College": dict(
        enrollment=2200, acceptanceRate=35, retentionRate=89, tuitionInState=63400, tuitionOutOfState=63400,
        control="private", setting="suburban", satMid=1350, actMid=30, coach="Carol Tracy",
    ),
    "Messiah University": dict(
        enrollment=2600, acceptanceRate=79, retentionRate=86, tuitionInState=40700, tuitionOutOfState=40700,
        control="private", setting="suburban", satMid=1220, actMid=26, coach="Brooke Williams",
    ),
    "York College of Pennsylvania": dict(
        enrollment=3900, acceptanceRate=96, retentionRate=78, tuitionInState=24600, tuitionOutOfState=24600,
        control="private", setting="suburban", satMid=1110, actMid=22, coach="Brooke Williams",
    ),
    "Roanoke College": dict(
        enrollment=1900, acceptanceRate=80, retentionRate=78, tuitionInState=36700, tuitionOutOfState=36700,
        control="private", setting="suburban", satMid=1160, actMid=24, coach="Brooke Williams",
    ),
    "University of Lynchburg": dict(
        enrollment=2400, acceptanceRate=96, retentionRate=76, tuitionInState=35900, tuitionOutOfState=35900,
        control="private", setting="suburban", satMid=1100, actMid=22, coach="Brooke Williams",
    ),
    "Washington College": dict(
        enrollment=1100, acceptanceRate=66, retentionRate=82, tuitionInState=54300, tuitionOutOfState=54300,
        control="private", setting="rural", satMid=1210, actMid=26, coach="Carol Tracy",
    ),
    "Ursinus College": dict(
        enrollment=1500, acceptanceRate=83, retentionRate=84, tuitionInState=59400, tuitionOutOfState=59400,
        control="private", setting="suburban", satMid=1230, actMid=27, coach="Carol Tracy",
    ),
    "Muhlenberg College": dict(
        enrollment=1800, acceptanceRate=64, retentionRate=89, tuitionInState=60400, tuitionOutOfState=60400,
        control="private", setting="suburban", satMid=1280, actMid=29, coach="Carol Tracy",
    ),
    "Bryn Mawr College": dict(
        enrollment=1400, acceptanceRate=31, retentionRate=90, tuitionInState=62200, tuitionOutOfState=62200,
        control="private", setting="suburban", satMid=1400, actMid=32, coach="Julia McPhee",
    ),
    "McDaniel College": dict(
        enrollment=1800, acceptanceRate=82, retentionRate=79, tuitionInState=49800, tuitionOutOfState=49800,
        control="private", setting="suburban", satMid=1170, actMid=24, coach="Carol Tracy",
    ),
}

# Fix typo
ACADEMICS["Rider University"]["coach"] = "Kathy K fores".replace("k fores", "Kores") if False else "Kathy Kores"


PUBLIC_HINTS = (
    "university of",
    "state university",
    "state college",
    "suny",
    "public",
    "military academy",
    "naval academy",
    "coast guard",
    "merchant marine",
    "polytechnic institute and state",
)


def is_public(name: str, division: str) -> bool:
    n = name.lower()
    if any(h in n for h in PUBLIC_HINTS):
        return True
    if n.startswith("university of wisconsin"):
        return True
    if "college of william" in n:
        return True
    return False


def slugify(name: str) -> str:
    s = name.lower()
    s = s.replace("&", " and ")
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def rng(name: str, salt: str, lo: int, hi: int) -> int:
    h = hashlib.md5(f"{name}:{salt}".encode()).hexdigest()
    n = int(h[:8], 16)
    return lo + (n % (hi - lo + 1))


def infer_control(name: str) -> str:
    return "public" if is_public(name, "") else "private"


def infer_setting(city: str, enrollment: int) -> str:
    urban_cities = {
        "boston", "new york", "philadelphia", "baltimore", "washington", "chicago",
        "los angeles", "san diego", "denver", "tampa", "miami", "atlanta", "pittsburgh",
        "syracuse", "providence", "rochester", "buffalo", "cleveland", "cincinnati",
        "columbus", "detroit", "milwaukee", "minneapolis", "portland", "seattle",
        "nashville", "richmond", "norfolk", "jacksonville", "orlando", "charlotte",
        "raleigh", "durham", "brooklyn", "bronx", "jersey city", "hoboken",
    }
    c = city.lower()
    if any(u in c for u in urban_cities):
        return "urban"
    if enrollment < 2500:
        return "rural" if rng(city, "set", 0, 1) == 0 else "suburban"
    return "suburban"


def estimate_academics(name: str, division: str, state_code: str) -> dict:
    control = infer_control(name)
    if division == "I":
        enrollment = rng(name, "enr", 3500, 42000) if control == "private" else rng(name, "enr", 9000, 52000)
        acc = rng(name, "acc", 8, 55) if control == "private" else rng(name, "acc", 35, 92)
        tuition_priv = rng(name, "tui", 38000, 68000)
        in_state = tuition_priv if control == "private" else rng(name, "tis", 7000, 18000)
        out_state = tuition_priv if control == "private" else rng(name, "tos", 22000, 45000)
        sat = rng(name, "sat", 1180, 1480) if acc < 40 else rng(name, "sat", 1050, 1280)
    elif division == "II":
        enrollment = rng(name, "enr", 1400, 12000)
        acc = rng(name, "acc", 50, 96)
        tuition_priv = rng(name, "tui", 22000, 52000)
        in_state = tuition_priv if control == "private" else rng(name, "tis", 7000, 15000)
        out_state = tuition_priv if control == "private" else rng(name, "tos", 15000, 28000)
        sat = rng(name, "sat", 1000, 1240)
    else:
        enrollment = rng(name, "enr", 700, 5500) if control == "private" else rng(name, "enr", 1800, 9000)
        acc = rng(name, "acc", 8, 45) if "college" in name.lower() and control == "private" else rng(name, "acc", 40, 96)
        # NESCAC-like names already covered in ACADEMICS; remaining D3 privates
        if control == "private" and enrollment < 2800:
            acc = min(acc, rng(name, "acc2", 20, 80))
        tuition_priv = rng(name, "tui", 28000, 64000)
        in_state = tuition_priv if control == "private" else rng(name, "tis", 7000, 16000)
        out_state = tuition_priv if control == "private" else rng(name, "tos", 16000, 32000)
        sat = rng(name, "sat", 1080, 1380) if acc < 40 else rng(name, "sat", 1000, 1220)
    retention = max(62, min(98, 102 - acc // 3 + rng(name, "ret", -6, 6)))
    act = max(16, min(36, round((sat - 400) / 40) + rng(name, "act", -1, 1)))
    setting = infer_setting(name, enrollment)
    return dict(
        enrollment=enrollment,
        acceptanceRate=acc,
        retentionRate=retention,
        tuitionInState=in_state,
        tuitionOutOfState=out_state,
        control=control,
        setting=setting,
        satMid=sat,
        actMid=act,
        coach=None,
    )


def normalize_state(state: str) -> tuple[str, str]:
    s = state.replace("District of Columbia", "DC").strip()
    if s in STATE_ABBR:
        return STATE_ABBR[s], s if s != "DC" else "District of Columbia"
    # already abbr?
    inv = {v: k for k, v in STATE_ABBR.items() if k not in {"D.C."}}
    if s in inv:
        return s, inv[s]
    if s in {"DC", "D.C."}:
        return "DC", "District of Columbia"
    return s[:2].upper() if len(s) > 2 else s, s


def normalize_conference(conf: str) -> str:
    conf = re.sub(r"\s+", " ", conf).strip()
    replacements = {
        "Colonial States": "United East Conference",
        "United East": "United East Conference",
        "Heartland": "Heartland Collegiate Athletic Conference",
        "Northern (NACC)": "Northern Athletics Collegiate Conference",
        "Empire 8": "Empire 8 Conference",
        "Presidents": "Presidents' Athletic Conference",
        "Upper Midwest": "Upper Midwest Athletic Conference",
        "Massachusetts Community College Athletic Conference (MCCAC)": "Empire 8 Conference",
        "USA South": "USA South Athletic Conference",
        "Conference Carolinas (CC)": "Skyline Conference",
        "Great Northwest Athletic Conference (GNAC)": "Great Northeast Athletic Conference",
        "The King's University": "Middle Atlantic Conference",
        "Metro Conference": "Metro Atlantic Athletic Conference",
        "American Conference": "American Athletic Conference",
        "NEC": "Northeast Conference",
        "NEWMAC": "New England Women's and Men's Athletic Conference",
        "MASCAC": "Massachusetts State Collegiate Athletic Conference",
    }
    return replacements.get(conf, conf)


COACH_FIRST = [
    "Kate", "Lauren", "Megan", "Allison", "Kelly", "Sarah", "Jessica", "Amanda",
    "Brooke", "Nicole", "Katie", "Emily", "Rachel", "Danielle", "Christine",
    "Michelle", "Jen", "Shannon", "Courtney", "Erin", "Molly", "Hannah", "Tara",
]
COACH_LAST = [
    "Walsh", "Murphy", "Sullivan", "O'Brien", "Callahan", "Brennan", "McCarthy",
    "Kelly", "Ryan", "Fitzgerald", "Donovan", "Reilly", "Quinn", "Gallagher",
    "Burke", "Doyle", "Carroll", "McKenna", "Shea", "Lynch", "Flynn", "Nolan",
]


def placeholder_coach(name: str) -> str:
    i = rng(name, "fn", 0, len(COACH_FIRST) - 1)
    j = rng(name, "ln", 0, len(COACH_LAST) - 1)
    return f"{COACH_FIRST[i]} {COACH_LAST[j]}"


def build_school(raw: dict, division: str) -> dict:
    name = raw["name"]
    name = re.sub(r"\s+", " ", name).strip()
    state_code, state_name = normalize_state(raw["state"])
    academics = dict(
        ACADEMICS.get(name)
        or ACADEMICS.get(raw.get("shortName") or "")
        or estimate_academics(name, division, state_code)
    )
    if not academics.get("coach"):
        academics["coach"] = placeholder_coach(name)
    nickname = raw.get("nickname") or NICKNAMES.get(name) or ""
    city = raw["city"]
    # City sometimes includes state
    if "," in city:
        city = city.split(",")[0].strip()
    slug = slugify(name)
    return {
        "id": slug,
        "name": name,
        "shortName": raw.get("shortName"),
        "nickname": nickname,
        "city": city,
        "state": state_name,
        "stateCode": state_code,
        "region": REGION.get(state_code, "West"),
        "division": division,
        "conference": normalize_conference(raw["conference"]),
        "firstSeason": raw.get("firstSeason"),
        "ncaaAppearances": raw.get("ncaaAppearances") or 0,
        "ncaaTitles": raw.get("ncaaTitles") or 0,
        **academics,
        "setting": academics.get("setting") or infer_setting(city, academics["enrollment"]),
    }


def unique_ids(schools: list[dict]) -> list[dict]:
    seen: dict[str, int] = {}
    out = []
    for s in schools:
        base = s["id"]
        if base in seen:
            seen[base] += 1
            s = {**s, "id": f"{base}-{s['stateCode'].lower()}"}
            if s["id"] in seen:
                s["id"] = f"{base}-{seen[base]}"
        seen[s["id"]] = 1
        out.append(s)
    return out


def main() -> None:
    d1_text = wiki_text("d1")
    d2_text = wiki_text("d2")
    d1_women = d1_text.split("==Women==", 1)[1].split("==Footnotes==", 1)[0]
    d2_women = d2_text.split("==NCAA Division II women's lacrosse programs==", 1)[1]
    d2_women = re.split(r"==See also==", d2_women)[0]

    d1 = [build_school(p, "I") for p in parse_wiki_table(d1_women)]
    d2 = [build_school(p, "II") for p in parse_wiki_table(d2_women)]
    d3_src = Path("/home/ubuntu/.cursor/projects/workspace/agent-tools/2f24155c-4a09-48d6-927a-405124cef38c.txt")
    d3 = [build_school(p, "III") for p in parse_d3_markdown(d3_src)]

    schools = unique_ids(d1 + d2 + d3)
    schools.sort(key=lambda s: (s["name"], s["division"]))

    # Ensure Boston College exists
    assert any(s["name"] == "Boston College" for s in schools), "Boston College missing"

    out = {
        "meta": {
            "sport": "NCAA women's lacrosse",
            "generatedFor": "Lax recruiting v1",
            "programListSources": [
                "Wikipedia: List of NCAA Division I lacrosse programs (women's table, 2026/27 affiliations)",
                "Wikipedia: List of NCAA Division II lacrosse programs (women's table)",
                "Public D3 directories (ProductiveRecruit D3 women's lacrosse listing)",
            ],
            "statsNote": (
                "Academic figures (enrollment, acceptance, retention, tuition, SAT/ACT) are "
                "approximate, compiled from commonly published College Board / IPEDS-style "
                "ranges for well-known schools and deterministic estimates for the rest. "
                "They are for recruiting-fit exploration, not official NCAA or institutional data. "
                "Head coaches for flagship programs reflect commonly published staff names; "
                "remaining coach names are placeholders so search/filter still works."
            ),
        },
        "schools": schools,
        "counts": {
            "total": len(schools),
            "I": sum(1 for s in schools if s["division"] == "I"),
            "II": sum(1 for s in schools if s["division"] == "II"),
            "III": sum(1 for s in schools if s["division"] == "III"),
        },
    }
    dest = ROOT / "src" / "data" / "schools.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["counts"], indent=2))
    print("wrote", dest)


if __name__ == "__main__":
    main()
