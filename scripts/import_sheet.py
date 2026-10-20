#!/usr/bin/env python3
"""Rebuild src/data/schools.json from the Google Sheet export.

The sheet is the only source for coach and academic fields. Existing school
ids are reused when the sheet names the same school, so saved notes and
targets still resolve. Schools already on the site but missing from the sheet
stay listed by name, division, conference, and location, with coach and stat
fields cleared.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET = Path(__file__).resolve().parent / "schools_from_sheet.csv"
CATALOG = ROOT / "src" / "data" / "schools.json"

STATE_ABBR = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "district of columbia": "DC",
    "d.c.": "DC",
    "dc": "DC",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
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
    "KS": "Midwest",
    "NE": "Midwest",
    "ND": "Midwest",
    "SD": "Midwest",
    "CO": "West",
    "UT": "West",
    "AZ": "West",
    "CA": "West",
    "OR": "West",
    "WA": "West",
    "ID": "West",
    "NV": "West",
    "NM": "West",
    "MT": "West",
    "WY": "West",
    "HI": "West",
    "AK": "West",
}

# Sheet spelling -> existing catalog id, after norm().
ALIASES = {
    "penn state": "pennsylvania-state-university",
    "virginia tech": "virginia-polytechnic-institute-and-state-university",
    "rutgers university": "rutgers-university-new-brunswick",
    "siena college": "siena-university",
    "marist college": "marist-university",
    "mercy college": "mercy-university",
    "william and mary": "college-of-william-and-mary",
    "university of maryland": "university-of-maryland-college-park",
    "elms college": "college-of-our-lady-of-the-elms",
    "edgewood college": "edgewood-university",
    "manhattanville college": "manhattanville-university",
    "alfred state college": "suny-college-of-technology-at-alfred",
    "north carolina wesleyan college": "north-carolina-wesleyan-university",
    "st john fisher college": "st-john-fisher-university",
    "cairn university": "cairn-university-langhorne",
    "hobart and william smith college": "hobart-william-smith-colleges",
    "hobart and william smith colleges": "hobart-william-smith-colleges",
    "claremont mudd scripps colleges": "claremont-mckenna-harvey-mudd-scripps",
    "sewanee the university of the south": "the-university-of-the-south",
    "fairleigh dickinson university college at florham": "fairleigh-dickinson-university-florham-campus",
    "suny fredonia": "suny-at-fredonia",
    "suny college at old westbury": "suny-old-westbury",
    "suny purchase college": "suny-at-purchase-college",
    "suny farmingdale state college": "farmingdale-state-college",
    "suny binghamton university": "binghamton-university",
    "suny stony brook university": "stony-brook-university",
    "suny university at albany": "university-at-albany",
    "suny cortland": "state-university-of-new-york-at-cortland",
    "suny geneseo": "suny-college-at-geneseo",
    "suny new paltz": "state-university-of-new-york-at-new-paltz",
    "suny oswego": "state-university-of-new-york-at-oswego",
    "suny plattsburgh": "state-university-of-new-york-at-plattsburgh",
    "suny potsdam": "suny-college-at-potsdam",
    "suny canton": "suny-college-of-technology-at-canton",
    "suny college at brockport": "suny-brockport",
    "suny college at oneonta": "suny-oneonta",
    "university of alabama huntsville": "university-of-alabama-in-huntsville",
    "east stroudsburg university of pennsylvania": "east-stroudsburg-university",
    "west chester university of pennsylvania": "west-chester-university",
    "bloomsburg university of pennsylvania": "commonwealth-university-bloomsburg",
    "kutztown university of pennsylvania": "kutztown-university",
    "millersville university of pennsylvania": "millersville-university",
    "shippensburg university of pennsylvania": "shippensburg-university",
    "lock haven university": "commonwealth-university-lock-haven",
    "emmanuel college georgia": "emmanuel-university",
    "westminster college utah": "westminster-university",
    "vermont state university castleton": "castleton-university",
    "flagler college st augustine": "flagler-college",
    "pomona pitzer colleges": "pomona-college",
    "bryn athyn college": "bryn-athyn-college-of-the-new-church",
    "massachusetts institute of technology mit": "massachusetts-institute-of-technology",
    "rensselaer polytechnic institute rpi": "rensselaer-polytechnic-institute",
    "university of pennsylvania penn": "university-of-pennsylvania",
}

DIVISIONS = {"NCAA D1": "I", "NCAA D2": "II", "NCAA D3": "III"}
SHEET_FIELDS = (
    "enrollment",
    "acceptanceRate",
    "retentionRate",
    "graduationRate",
    "satRange",
    "satMean",
    "testPolicy",
    "coach",
    "coachEmail",
)


def norm(name: str) -> str:
    text = name.lower().replace("&", " and ")
    text = text.replace("–", " ").replace("—", " ").replace("-", " ")
    text = text.replace("'", "").replace("’", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text.startswith("the "):
        text = text[4:]
    return text


def slugify(name: str) -> str:
    text = name.lower().replace("&", " and ")
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def strip_state(key: str) -> str | None:
    for state in sorted(STATE_ABBR, key=len, reverse=True):
        suffix = " " + state
        if key.endswith(suffix) and key[: -len(suffix)].strip():
            return key[: -len(suffix)].strip()
    return None


def first_number(raw: str) -> float | None:
    match = re.search(r"\d[\d,]*(?:\.\d+)?", raw)
    if not match:
        return None
    return float(match.group(0).replace(",", ""))


def parse_retention(raw: str) -> float | None:
    text = raw.strip()
    if not text:
        return None
    labeled = re.search(r"Retention:\s*([\d.]+)\s*%", text, re.I)
    if labeled:
        return float(labeled.group(1))
    subtracted = re.search(r"100%\s*-\s*([\d.]+)\s*%\s*Retention", text, re.I)
    if subtracted:
        return float(subtracted.group(1))
    return first_number(text)


def parse_range_mid(raw: str) -> float | None:
    match = re.search(r"(\d{3,4})\s*[-–—]\s*(\d{3,4})", raw)
    if not match:
        return None
    low = int(match.group(1))
    high = int(match.group(2))
    return (low + high) / 2


def clean_email(raw: str) -> str:
    text = raw.strip()
    if not text:
        return ""
    if "@" in text:
        return text
    if re.search(r"\([^)]+\)", text):
        return text
    return ""


def clean_coach(raw: str) -> tuple[str, str | None]:
    """Return (display name, original parenthetical form if it was collapsed)."""
    text = raw.strip()
    text = re.sub(r"^Women['’]s:\s*", "", text)
    collapsed = text
    previous = None
    while previous != collapsed:
        previous = collapsed
        collapsed = re.sub(r"(\([^)]*\))(?:\s*\1)+", r"\1", collapsed)
    collapsed = re.sub(r"\s+", " ", collapsed).strip()
    if collapsed != text:
        return collapsed, text
    return collapsed, None


def parse_location(raw: str) -> tuple[str, str, str]:
    text = raw.strip()
    if "," not in text:
        return text, "", ""
    city, state = [part.strip() for part in text.rsplit(",", 1)]
    code = STATE_ABBR.get(state.lower(), "")
    if state.lower() in {"district of columbia", "d.c.", "dc"}:
        state = "District of Columbia"
    return city, state, code


def blank_stats() -> dict:
    return {
        "shortName": None,
        "nickname": "",
        "firstSeason": None,
        "ncaaAppearances": None,
        "ncaaTitles": None,
        "enrollment": None,
        "acceptanceRate": None,
        "retentionRate": None,
        "graduationRate": None,
        "tuitionInState": None,
        "tuitionOutOfState": None,
        "control": "",
        "setting": "",
        "satRange": "",
        "satMean": None,
        "satMid": None,
        "testPolicy": "",
        "actMid": None,
        "coach": "",
        "coachEmail": "",
    }


def load_sheet() -> list[list[str]]:
    with SHEET.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    header = rows[0]
    if len(header) != 14:
        raise SystemExit(f"expected 14 columns, found {len(header)}")
    padded = []
    for row in rows[1:]:
        if not row or not row[0].strip():
            continue
        padded.append((row + [""] * 14)[:14])
    return padded


def index_existing(schools: list[dict]) -> dict[str, list[dict]]:
    index: dict[str, list[dict]] = defaultdict(list)
    for school in schools:
        index[norm(school["name"])].append(school)
    return index


def pick(candidates: list[dict], state_code: str, division: str | None = None) -> str | None:
    if not candidates:
        return None
    if state_code:
        same_state = [school for school in candidates if school.get("stateCode") == state_code]
        if len(same_state) == 1:
            return same_state[0]["id"]
        if len(same_state) == 0:
            return None
        candidates = same_state
    if division:
        same_division = [school for school in candidates if school.get("division") == division]
        if len(same_division) == 1:
            return same_division[0]["id"]
    if len(candidates) == 1:
        return candidates[0]["id"]
    return None


def match_id(
    name: str,
    state_code: str,
    division: str,
    index: dict[str, list[dict]],
    by_id: dict[str, dict],
) -> str | None:
    full = norm(name)
    no_paren = norm(re.sub(r"\([^)]*\)", " ", name))
    keys = [full]
    if no_paren != full:
        keys.append(no_paren)
    stripped = strip_state(full)
    if stripped and stripped not in keys:
        keys.append(stripped)
    for key in list(keys):
        alias = ALIASES.get(key)
        if alias and alias in by_id:
            school = by_id[alias]
            if not state_code or school.get("stateCode") == state_code:
                return alias
    parts = [part.strip() for part in re.split(r"\s+[–—]\s+|\s+-\s+", name) if part.strip()]
    # Exact name of a dash segment can match ("The University of the South").
    # Do not alias a segment: "University of Maryland – Baltimore County" must
    # not inherit the "University of Maryland" -> College Park alias.
    for part in parts:
        part_key = norm(part)
        if part_key not in keys:
            keys.append(part_key)
    for key in keys:
        chosen = pick(index.get(key, []), state_code, division)
        if chosen:
            return chosen
    return None


def sheet_record(row: list[str], existing_id: str | None) -> tuple[dict, dict | None]:
    name = row[0].strip()
    city, state, state_code = parse_location(row[1])
    control_raw = row[2].strip().lower()
    control = control_raw if control_raw in {"public", "private"} else ""
    conference = row[3].strip()
    division = DIVISIONS[row[4].strip()]
    enrollment = first_number(row[5]) if row[5].strip() else None
    acceptance = first_number(row[6]) if row[6].strip() else None
    sat_range = row[7].strip()
    sat_mean = first_number(row[8]) if row[8].strip() else None
    sat_mid = sat_mean if sat_mean is not None else parse_range_mid(sat_range)
    test_policy = row[9].strip()
    graduation = first_number(row[10]) if row[10].strip() else None
    retention = parse_retention(row[11])
    coach, garbled_from = clean_coach(row[12])
    email = clean_email(row[13])
    record = {
        "id": existing_id or slugify(name),
        "_matched": existing_id is not None,
        "name": name,
        "city": city,
        "state": state,
        "stateCode": state_code,
        "region": REGION.get(state_code, ""),
        "division": division,
        "conference": conference,
        **blank_stats(),
        "enrollment": int(enrollment) if enrollment is not None else None,
        "acceptanceRate": acceptance,
        "retentionRate": retention,
        "graduationRate": graduation,
        "control": control,
        "satRange": sat_range,
        "satMean": int(sat_mean) if sat_mean is not None else None,
        "satMid": sat_mid,
        "testPolicy": test_policy,
        "coach": coach,
        "coachEmail": email,
    }
    change = None
    if garbled_from is not None:
        change = {
            "school": name,
            "division": division,
            "before": garbled_from,
            "after": coach,
        }
    return record, change


def fresh_id(base: str, state_code: str, used: set[str], by_id: dict[str, dict]) -> str:
    candidates = [base]
    if state_code:
        candidates.append(f"{base}-{state_code.lower()}")
    n = 2
    while True:
        for candidate in candidates:
            if candidate not in used and candidate not in by_id:
                return candidate
        candidates = [f"{base}-{n}"]
        n += 1


def allocate_ids(records: list[dict], by_id: dict[str, dict]) -> None:
    """Matched rows keep the existing id. A second division listing gets a suffix.

    Brand-new schools never take an id that already belongs to the catalog.
    """
    used: set[str] = set()
    for record in records:
        preferred = record["id"]
        matched = record.pop("_matched")
        if matched and preferred not in used:
            used.add(preferred)
            continue
        if matched:
            division = {"I": "d1", "II": "d2", "III": "d3"}[record["division"]]
            n = 0
            while True:
                candidate = f"{preferred}-{division}" if n == 0 else f"{preferred}-{division}-{n + 1}"
                n += 1
                if candidate not in used and candidate not in by_id:
                    record["id"] = candidate
                    used.add(candidate)
                    break
            continue
        assigned = fresh_id(preferred, record.get("stateCode") or "", used, by_id)
        record["id"] = assigned
        used.add(assigned)


def site_only_record(school: dict) -> dict:
    return {
        "id": school["id"],
        "name": school["name"],
        "city": school.get("city") or "",
        "state": school.get("state") or "",
        "stateCode": school.get("stateCode") or "",
        "region": school.get("region") or "",
        "division": school["division"],
        "conference": school.get("conference") or "",
        **blank_stats(),
    }


def is_blank(record: dict) -> bool:
    for field in SHEET_FIELDS:
        value = record.get(field)
        if value is None or value == "":
            return True
    return False


def main() -> None:
    previous = json.loads(CATALOG.read_text())
    existing = previous["schools"]
    by_id = {school["id"]: school for school in existing}
    index = index_existing(existing)
    rows = load_sheet()

    records: list[dict] = []
    changes: list[dict] = []
    claimed: set[str] = set()
    for row in rows:
        city, _state, state_code = parse_location(row[1])
        del city
        division = DIVISIONS[row[4].strip()]
        preferred = match_id(row[0].strip(), state_code, division, index, by_id)
        record, change = sheet_record(row, preferred)
        if preferred:
            claimed.add(preferred)
        records.append(record)
        if change:
            changes.append(change)

    allocate_ids(records, by_id)
    claimed_after = {record["id"] for record in records}
    # An existing id claimed before suffixing can still be unused if a later row took it
    # and the first row was retitled. Recompute from final ids.
    final_ids = {record["id"] for record in records}
    leftovers = [site_only_record(school) for school in existing if school["id"] not in final_ids]
    leftovers.sort(key=lambda school: school["name"])
    schools = records + leftovers

    counts = {"total": len(schools), "I": 0, "II": 0, "III": 0}
    for school in schools:
        counts[school["division"]] += 1

    blank_schools = sum(1 for school in schools if is_blank(school))
    field_blanks = {field: sum(1 for school in schools if school.get(field) in (None, "")) for field in SHEET_FIELDS}

    payload = {
        "meta": {
            "sport": "NCAA women's lacrosse",
            "generatedFor": "Lax recruiting sheet import",
            "programListSources": [
                "Family Google Sheet export (scripts/schools_from_sheet.csv)",
                "Schools already on the site but absent from the sheet stay listed by name, division, conference, and location only",
            ],
            "statsNote": "Enrollment, admit rate, SAT, test policy, graduation rate, retention, coach, and coach email come only from the sheet. Blank sheet cells stay blank. Tuition, campus setting, nicknames, and NCAA totals are not in the sheet and are not estimated.",
        },
        "schools": schools,
        "counts": counts,
    }
    CATALOG.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    adrian = next(school for school in schools if school["id"] == "adrian-college")
    assert adrian["coach"] == "Erika Ratti", adrian["coach"]
    assert adrian["acceptanceRate"] == 73.0, adrian["acceptanceRate"]
    assert adrian["retentionRate"] == 80.0, adrian["retentionRate"]
    assert adrian["enrollment"] == 1732, adrian["enrollment"]
    assert adrian["coachEmail"] == "eratti@adrian.edu"
    boston = next(school for school in schools if school["id"] == "boston-college")
    assert boston["coach"] == "Acacia Walker-Khan"
    assert boston["coachEmail"] == "athletics@bc.edu (General Athletics)"
    assert boston["acceptanceRate"] == 15.7
    northwestern = next(school for school in schools if school["name"] == "Northwestern University")
    assert northwestern["coach"] == "Kelly (Amonte Hiller)", northwestern["coach"]
    assert all("McCarthy" not in (school["coach"] or "") for school in schools)

    report = {
        "sheetRows": len(rows),
        "siteTotal": counts,
        "blankSchools": blank_schools,
        "fieldBlanks": field_blanks,
        "tuitionBlank": sum(1 for school in schools if school["tuitionInState"] is None),
        "garbled": changes,
        "siteOnly": [
            {
                "id": school["id"],
                "name": school["name"],
                "division": school["division"],
                "conference": school["conference"],
                "city": school["city"],
                "state": school["state"],
            }
            for school in leftovers
        ],
        "newSchools": sorted(
            school["name"] + " [" + school["division"] + "] " + school["id"]
            for school in records
            if school["id"] not in by_id
        ),
    }
    report_path = Path("/tmp/sheet-import-report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("sheetRows", "siteTotal", "blankSchools", "fieldBlanks", "tuitionBlank")}, indent=2))
    print("garbled", len(changes))
    print("siteOnly", len(leftovers))
    print("new", len(report["newSchools"]))
    print("report", report_path)


if __name__ == "__main__":
    main()
