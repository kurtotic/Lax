import type { Dispatch, ReactNode, SetStateAction } from "react";
import { X } from "lucide-react";
import { allConferences, allRegions, allStates } from "../data/catalog";
import { activeFilterCount, defaultFilters } from "../lib/filters";
import { stateNames } from "../lib/format";
import type { Division, Filters, Region } from "../types";

const divisions: Division[] = ["I", "II", "III"];

export function FilterPanel({
  filters,
  setFilters,
  resultCount,
  mobileOpen,
  onClose,
}: {
  filters: Filters;
  setFilters: Dispatch<SetStateAction<Filters>>;
  resultCount: number;
  mobileOpen?: boolean;
  onClose?: () => void;
}) {
  const count = activeFilterCount(filters);

  const toggle = <T,>(key: keyof Filters, value: T) => {
    setFilters((prev) => {
      const list = prev[key] as T[];
      const next = list.includes(value)
        ? list.filter((item) => item !== value)
        : [...list, value];
      return { ...prev, [key]: next };
    });
  };

  const body = (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="display text-xl">Filters</h2>
          <p className="text-xs text-muted">
            {resultCount} programs · {count} active
          </p>
        </div>
        <button
          type="button"
          onClick={() => setFilters({ ...defaultFilters, sort: filters.sort })}
          className="text-sm font-medium text-field hover:underline"
        >
          Clear all
        </button>
      </div>

      <Section title="Division">
        <div className="flex flex-wrap gap-2">
          {divisions.map((division) => (
            <Chip
              key={division}
              on={filters.divisions.includes(division)}
              onClick={() => toggle("divisions", division)}
            >
              D{division}
            </Chip>
          ))}
        </div>
      </Section>

      <Section title="Region">
        <div className="flex flex-wrap gap-2">
          {allRegions.map((region) => (
            <Chip
              key={region}
              on={filters.regions.includes(region)}
              onClick={() => toggle("regions", region as Region)}
            >
              {region}
            </Chip>
          ))}
        </div>
      </Section>

      <Section title="School type">
        <div className="flex flex-wrap gap-2">
          <Chip
            on={filters.control === "public"}
            onClick={() =>
              setFilters((p) => ({ ...p, control: p.control === "public" ? "" : "public" }))
            }
          >
            Public
          </Chip>
          <Chip
            on={filters.control === "private"}
            onClick={() =>
              setFilters((p) => ({ ...p, control: p.control === "private" ? "" : "private" }))
            }
          >
            Private
          </Chip>
          {(["urban", "suburban", "rural"] as const).map((setting) => (
            <Chip
              key={setting}
              on={filters.setting === setting}
              onClick={() =>
                setFilters((p) => ({ ...p, setting: p.setting === setting ? "" : setting }))
              }
            >
              {setting}
            </Chip>
          ))}
        </div>
      </Section>

      <Section title="Enrollment">
        <Select
          value={filters.enrollment}
          onChange={(enrollment) => setFilters((p) => ({ ...p, enrollment }))}
          options={[
            ["", "Any size"],
            ["lt3", "Under 3,000"],
            ["3to10", "3,000 – 10,000"],
            ["10to20", "10,000 – 20,000"],
            ["gt20", "20,000+"],
          ]}
        />
      </Section>

      <Section title="SAT mid-range">
        <Select
          value={filters.sat}
          onChange={(sat) => setFilters((p) => ({ ...p, sat }))}
          options={[
            ["", "Any"],
            ["1200", "1200+"],
            ["1300", "1300+"],
            ["1400", "1400+"],
          ]}
        />
      </Section>

      <Section title="State">
        <select
          value={filters.states[0] ?? ""}
          onChange={(event) =>
            setFilters((p) => ({
              ...p,
              states: event.target.value ? [event.target.value] : [],
            }))
          }
          className="w-full rounded-xl border border-line bg-card px-3 py-2 text-sm"
        >
          <option value="">All states</option>
          {allStates.map((code) => (
            <option key={code} value={code}>
              {stateNames[code] ?? code} ({code})
            </option>
          ))}
        </select>
      </Section>

      <Section title="Conference">
        <select
          value={filters.conferences[0] ?? ""}
          onChange={(event) =>
            setFilters((p) => ({
              ...p,
              conferences: event.target.value ? [event.target.value] : [],
            }))
          }
          className="w-full rounded-xl border border-line bg-card px-3 py-2 text-sm"
        >
          <option value="">All conferences</option>
          {allConferences.map((conference) => (
            <option key={conference} value={conference}>
              {conference}
            </option>
          ))}
        </select>
      </Section>
    </div>
  );

  if (mobileOpen !== undefined) {
    return (
      <div
        className={`fixed inset-0 z-50 lg:hidden ${mobileOpen ? "" : "pointer-events-none"}`}
      >
        <button
          type="button"
          className={`absolute inset-0 bg-ink/40 transition ${mobileOpen ? "opacity-100" : "opacity-0"}`}
          aria-label="Close filters"
          onClick={onClose}
        />
        <aside
          className={`absolute top-0 right-0 flex h-full w-[min(100%,22rem)] flex-col bg-paper shadow-2xl transition-transform ${
            mobileOpen ? "translate-x-0" : "translate-x-full"
          }`}
        >
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <span className="font-semibold">Refine programs</span>
            <button type="button" onClick={onClose} className="rounded-full p-1 hover:bg-line/60">
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4">{body}</div>
        </aside>
      </div>
    );
  }

  return <aside className="hidden lg:block">{body}</aside>;
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h3 className="mb-2 text-[11px] font-semibold tracking-[0.16em] text-muted uppercase">
        {title}
      </h3>
      {children}
    </section>
  );
}

function Chip({
  on,
  onClick,
  children,
}: {
  on: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-2.5 py-1 text-xs font-medium capitalize ${
        on ? "border-field bg-field text-paper" : "border-line bg-card text-ink hover:border-moss/40"
      }`}
    >
      {children}
    </button>
  );
}

function Select<T extends string>({
  value,
  onChange,
  options,
}: {
  value: T;
  onChange: (value: T) => void;
  options: [T, string][];
}) {
  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value as T)}
      className="w-full rounded-xl border border-line bg-card px-3 py-2 text-sm"
    >
      {options.map(([val, label]) => (
        <option key={val || "any"} value={val}>
          {label}
        </option>
      ))}
    </select>
  );
}
