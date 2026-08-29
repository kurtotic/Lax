import catalog from "./schools.json";
import type { CatalogFile, School } from "../types";

const data = catalog as CatalogFile;

export const schools: School[] = data.schools;
export const catalogMeta = data.meta;
export const catalogCounts = data.counts;

export const schoolsById: Record<string, School> = Object.fromEntries(
  schools.map((school) => [school.id, school]),
);

export function getSchool(id: string): School | undefined {
  return schoolsById[id];
}

export const allStates = [...new Set(schools.map((s) => s.stateCode))].sort();
export const allConferences = [...new Set(schools.map((s) => s.conference))].sort(
  (a, b) => a.localeCompare(b),
);
export const allRegions = [
  "Northeast",
  "Mid-Atlantic",
  "Southeast",
  "South",
  "Midwest",
  "West",
] as const;
