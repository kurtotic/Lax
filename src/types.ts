export type Division = "I" | "II" | "III";
export type Control = "public" | "private";
export type Setting = "urban" | "suburban" | "rural";
export type Region =
  | "Northeast"
  | "Mid-Atlantic"
  | "Southeast"
  | "South"
  | "Midwest"
  | "West";

export interface School {
  id: string;
  name: string;
  shortName: string | null;
  nickname: string;
  city: string;
  state: string;
  stateCode: string;
  region: Region;
  division: Division;
  conference: string;
  firstSeason: number | null;
  ncaaAppearances: number;
  ncaaTitles: number;
  enrollment: number;
  acceptanceRate: number;
  retentionRate: number;
  tuitionInState: number;
  tuitionOutOfState: number;
  control: Control;
  setting: Setting;
  satMid: number;
  actMid: number;
  coach: string;
}

export interface CatalogFile {
  meta: {
    sport: string;
    generatedFor: string;
    programListSources: string[];
    statsNote: string;
  };
  schools: School[];
  counts: { total: number; I: number; II: number; III: number };
}

export interface Note {
  id: string;
  text: string;
  createdAt: string;
}

export interface PersistedState {
  notesBySchool: Record<string, Note[]>;
  targetIds: string[];
}

export type TuitionBasis = "inState" | "outOfState";

export type SortKey =
  | "name"
  | "acceptance"
  | "enrollment"
  | "tuition"
  | "retention"
  | "titles";

export interface Filters {
  query: string;
  divisions: Division[];
  regions: Region[];
  states: string[];
  conferences: string[];
  control: Control | "";
  setting: Setting | "";
  enrollment: "" | "lt3" | "3to10" | "10to20" | "gt20";
  acceptance: "" | "lt20" | "20to50" | "50to80" | "gt80";
  tuition: "" | "lt20" | "20to40" | "40to60" | "gt60";
  tuitionBasis: TuitionBasis;
  retention: "" | "80" | "90";
  sat: "" | "1200" | "1300" | "1400";
  sort: SortKey;
}
