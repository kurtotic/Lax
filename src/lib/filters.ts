import type { Filters, School } from "../types";

export const defaultFilters: Filters = {
  query: "",
  divisions: [],
  regions: [],
  states: [],
  conferences: [],
  control: "",
  setting: "",
  enrollment: "",
  acceptance: "",
  tuition: "",
  tuitionBasis: "outOfState",
  retention: "",
  sat: "",
  sort: "name",
};

export function activeFilterCount(filters: Filters): number {
  let n = 0;
  if (filters.query.trim()) n += 1;
  n += filters.divisions.length;
  n += filters.regions.length;
  n += filters.states.length;
  n += filters.conferences.length;
  if (filters.control) n += 1;
  if (filters.setting) n += 1;
  if (filters.enrollment) n += 1;
  if (filters.acceptance) n += 1;
  if (filters.tuition) n += 1;
  if (filters.retention) n += 1;
  if (filters.sat) n += 1;
  return n;
}

function inBucket<T extends string>(
  value: number,
  bucket: T,
  ranges: Record<Exclude<T, "">, [number, number]>,
): boolean {
  if (!bucket) return true;
  const range = ranges[bucket as Exclude<T, "">];
  if (!range) return true;
  return value >= range[0] && value < range[1];
}

const SEARCH_ALIASES: Record<string, string> = {
  "boston-college": "bc eagles chestnut hill",
  "university-of-north-carolina-at-chapel-hill": "unc carolina tar heels chapel hill",
  "university-of-maryland-college-park": "umd terps maryland",
  "pennsylvania-state-university": "penn state psu nittany",
  "university-of-virginia": "uva cavaliers",
  "virginia-polytechnic-institute-and-state-university": "virginia tech hokies vt",
  "university-of-southern-california": "usc trojans",
  "university-of-california-berkeley": "cal berkeley",
  "johns-hopkins-university": "jhu hopkins",
  "massachusetts-institute-of-technology": "mit",
  "university-of-pennsylvania": "upenn penn quakers",
  "united-states-naval-academy": "navy midshipmen usna",
  "united-states-military-academy": "army west point usma",
  "james-madison-university": "jmu dukes",
  "loyola-university-maryland": "loyola greyhounds",
};

export function haystack(school: School): string {
  return [
    school.name,
    school.shortName,
    school.nickname,
    school.city,
    school.state,
    school.stateCode,
    school.region,
    school.conference,
    school.coach,
    school.control,
    school.setting,
    `D${school.division}`,
    `Division ${school.division}`,
    school.id.replaceAll("-", " "),
    SEARCH_ALIASES[school.id] ?? "",
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

export function filterSchools(schools: School[], filters: Filters): School[] {
  const q = filters.query.trim().toLowerCase();
  const tokens = q ? q.split(/\s+/).filter(Boolean) : [];

  const tuitionOf = (school: School) =>
    filters.tuitionBasis === "inState"
      ? school.tuitionInState
      : school.tuitionOutOfState;

  let result = schools.filter((school) => {
    if (tokens.length) {
      const hay = haystack(school);
      if (!tokens.every((token) => hay.includes(token))) return false;
    }
    if (filters.divisions.length && !filters.divisions.includes(school.division)) {
      return false;
    }
    if (filters.regions.length && !filters.regions.includes(school.region)) {
      return false;
    }
    if (filters.states.length && !filters.states.includes(school.stateCode)) {
      return false;
    }
    if (
      filters.conferences.length &&
      !filters.conferences.includes(school.conference)
    ) {
      return false;
    }
    if (filters.control && school.control !== filters.control) return false;
    if (filters.setting && school.setting !== filters.setting) return false;
    if (
      !inBucket(school.enrollment, filters.enrollment, {
        lt3: [0, 3000],
        "3to10": [3000, 10000],
        "10to20": [10000, 20000],
        gt20: [20000, Infinity],
      })
    ) {
      return false;
    }
    if (
      !inBucket(school.acceptanceRate, filters.acceptance, {
        lt20: [0, 20],
        "20to50": [20, 50],
        "50to80": [50, 80],
        gt80: [80, Infinity],
      })
    ) {
      return false;
    }
    if (
      !inBucket(tuitionOf(school), filters.tuition, {
        lt20: [0, 20000],
        "20to40": [20000, 40000],
        "40to60": [40000, 60000],
        gt60: [60000, Infinity],
      })
    ) {
      return false;
    }
    if (filters.retention === "80" && school.retentionRate < 80) return false;
    if (filters.retention === "90" && school.retentionRate < 90) return false;
    if (filters.sat === "1200" && school.satMid < 1200) return false;
    if (filters.sat === "1300" && school.satMid < 1300) return false;
    if (filters.sat === "1400" && school.satMid < 1400) return false;
    return true;
  });

  result = [...result].sort((a, b) => {
    switch (filters.sort) {
      case "acceptance":
        return a.acceptanceRate - b.acceptanceRate;
      case "enrollment":
        return b.enrollment - a.enrollment;
      case "tuition":
        return tuitionOf(a) - tuitionOf(b);
      case "retention":
        return b.retentionRate - a.retentionRate;
      case "titles":
        return b.ncaaTitles - a.ncaaTitles || b.ncaaAppearances - a.ncaaAppearances;
      default:
        return a.name.localeCompare(b.name);
    }
  });

  return result;
}
