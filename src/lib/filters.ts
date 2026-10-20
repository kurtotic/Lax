import type { Filters, School } from "../types";

export const ACCEPTANCE_RANGE = { min: 0, max: 100 };
export const TUITION_RANGE = { min: 0, max: 70000 };
export const RETENTION_RANGE = { min: 0, max: 100 };

export const defaultFilters: Filters = {
  query: "",
  divisions: [],
  regions: [],
  states: [],
  conferences: [],
  control: "",
  setting: "",
  enrollment: "",
  acceptanceMin: ACCEPTANCE_RANGE.min,
  acceptanceMax: ACCEPTANCE_RANGE.max,
  tuitionMin: TUITION_RANGE.min,
  tuitionMax: TUITION_RANGE.max,
  tuitionBasis: "outOfState",
  retentionMin: RETENTION_RANGE.min,
  retentionMax: RETENTION_RANGE.max,
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
  if (
    filters.acceptanceMin > ACCEPTANCE_RANGE.min ||
    filters.acceptanceMax < ACCEPTANCE_RANGE.max
  ) {
    n += 1;
  }
  if (filters.tuitionMin > TUITION_RANGE.min || filters.tuitionMax < TUITION_RANGE.max) {
    n += 1;
  }
  if (
    filters.retentionMin > RETENTION_RANGE.min ||
    filters.retentionMax < RETENTION_RANGE.max
  ) {
    n += 1;
  }
  if (filters.sat) n += 1;
  return n;
}

function passesRange(
  value: number | null,
  min: number,
  max: number,
  bounds: { min: number; max: number },
): boolean {
  const unrestricted = min <= bounds.min && max >= bounds.max;
  if (value == null) return unrestricted;
  return value >= min && value <= max;
}

function compareNumbers(
  a: number | null,
  b: number | null,
  direction: "asc" | "desc",
): number {
  if (a == null && b == null) return 0;
  if (a == null) return 1;
  if (b == null) return -1;
  return direction === "asc" ? a - b : b - a;
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
    school.coachEmail,
    school.testPolicy,
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
    if (filters.regions.length && (!school.region || !filters.regions.includes(school.region))) {
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
    if (filters.enrollment) {
      if (school.enrollment == null) return false;
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
    }
    if (
      !passesRange(
        school.acceptanceRate,
        filters.acceptanceMin,
        filters.acceptanceMax,
        ACCEPTANCE_RANGE,
      )
    ) {
      return false;
    }
    if (
      !passesRange(tuitionOf(school), filters.tuitionMin, filters.tuitionMax, TUITION_RANGE)
    ) {
      return false;
    }
    if (
      !passesRange(
        school.retentionRate,
        filters.retentionMin,
        filters.retentionMax,
        RETENTION_RANGE,
      )
    ) {
      return false;
    }
    if (filters.sat) {
      const floor = Number(filters.sat);
      if (school.satMid == null || school.satMid < floor) return false;
    }
    return true;
  });

  result = [...result].sort((a, b) => {
    switch (filters.sort) {
      case "acceptance":
        return compareNumbers(a.acceptanceRate, b.acceptanceRate, "asc");
      case "enrollment":
        return compareNumbers(a.enrollment, b.enrollment, "desc");
      case "tuition":
        return compareNumbers(tuitionOf(a), tuitionOf(b), "asc");
      case "retention":
        return compareNumbers(a.retentionRate, b.retentionRate, "desc");
      case "titles":
        return (
          compareNumbers(a.ncaaTitles, b.ncaaTitles, "desc") ||
          compareNumbers(a.ncaaAppearances, b.ncaaAppearances, "desc")
        );
      default:
        return a.name.localeCompare(b.name);
    }
  });

  return result;
}
