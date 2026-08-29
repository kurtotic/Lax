import { useMemo, useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { catalogCounts, schools } from "../data/catalog";
import { activeFilterCount, defaultFilters, filterSchools } from "../lib/filters";
import type { Filters } from "../types";
import { EmptyState } from "../components/EmptyState";
import { FilterPanel } from "../components/FilterPanel";
import { SchoolCard } from "../components/SchoolCard";

export function BrowsePage() {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [mobileOpen, setMobileOpen] = useState(false);
  const results = useMemo(() => filterSchools(schools, filters), [filters]);
  const active = activeFilterCount(filters);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <section className="mb-8 overflow-hidden rounded-3xl bg-field px-5 py-8 text-paper sm:px-8">
        <p className="text-xs tracking-[0.22em] text-white/70 uppercase">NCAA women's lacrosse</p>
        <h1 className="display mt-2 max-w-2xl text-4xl leading-tight sm:text-5xl">
          Find the right program. Keep every conversation.
        </h1>
        <p className="mt-3 max-w-xl text-sm text-paper/75 sm:text-base">
          Search {catalogCounts.total} Division I, II, and III schools. Filter by academics and
          location, pin a ranked target list, and save dated notes on every outreach.
        </p>
        <label className="relative mt-6 block">
          <Search className="pointer-events-none absolute top-1/2 left-4 h-5 w-5 -translate-y-1/2 text-muted" />
          <input
            type="search"
            value={filters.query}
            onChange={(event) => setFilters((p) => ({ ...p, query: event.target.value }))}
            placeholder="Search school, city, conference, or coach — try Boston College"
            className="w-full rounded-2xl border-0 bg-white py-3.5 pr-4 pl-12 text-ink outline-none ring-white/40 placeholder:text-muted focus:ring-4"
          />
        </label>
        <div className="mt-4 flex flex-wrap gap-2 text-xs text-paper/80">
          <span className="rounded-full bg-white/10 px-3 py-1">{catalogCounts.I} D1</span>
          <span className="rounded-full bg-white/10 px-3 py-1">{catalogCounts.II} D2</span>
          <span className="rounded-full bg-white/10 px-3 py-1">{catalogCounts.III} D3</span>
        </div>
      </section>

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted">
          <span className="font-semibold text-ink">{results.length}</span> programs
          {active > 0 ? ` · ${active} filter${active === 1 ? "" : "s"} on` : ""}
        </p>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <span className="text-muted">Sort</span>
            <select
              value={filters.sort}
              onChange={(event) =>
                setFilters((p) => ({ ...p, sort: event.target.value as Filters["sort"] }))
              }
              className="rounded-full border border-line bg-card px-3 py-1.5 text-sm"
            >
              <option value="name">Name</option>
              <option value="acceptance">Most selective</option>
              <option value="enrollment">Largest</option>
              <option value="tuition">Lowest tuition</option>
              <option value="retention">Highest retention</option>
              <option value="titles">NCAA titles</option>
            </select>
          </label>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-full border border-line bg-card px-3 py-1.5 text-sm font-medium lg:hidden"
            onClick={() => setMobileOpen(true)}
          >
            <SlidersHorizontal className="h-4 w-4" />
            Filters{active ? ` (${active})` : ""}
          </button>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[16.5rem_minmax(0,1fr)]">
        <div className="hidden lg:block">
          <FilterPanel filters={filters} setFilters={setFilters} resultCount={results.length} />
        </div>
        <div className="space-y-3">
          {results.length === 0 ? (
            <EmptyState
              title="No programs match"
              body="Try a broader search, or clear filters to see the full NCAA women's lacrosse catalog."
              action={{
                label: "Clear filters",
                onClick: () => setFilters(defaultFilters),
              }}
            />
          ) : (
            results.map((school) => <SchoolCard key={school.id} school={school} />)
          )}
        </div>
      </div>
      <FilterPanel
        filters={filters}
        setFilters={setFilters}
        resultCount={results.length}
        mobileOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
      />
    </div>
  );
}
