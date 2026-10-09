import { Link } from "react-router-dom";
import type { School } from "../types";
import { divisionLabel, money, people, pct } from "../lib/format";
import { TargetButton } from "./TargetButton";

export function SchoolCard({ school }: { school: School }) {
  return (
    <article className="group relative rounded-2xl border border-line bg-white p-4 shadow-[0_1px_0_rgba(11,31,58,0.04)] transition hover:-translate-y-0.5 hover:border-field/30 hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <Link to={`/schools/${school.id}`} className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full px-2 py-0.5 text-[11px] font-semibold tracking-wide ${
                school.division === "I"
                  ? "bg-field text-white"
                  : school.division === "II"
                    ? "bg-field/10 text-field"
                    : "bg-ink/8 text-ink"
              }`}
            >
              {divisionLabel(school.division)}
            </span>
            <span className="text-xs text-muted">{school.conference}</span>
          </div>
          <h2 className="display text-xl leading-tight font-semibold text-ink group-hover:text-field">
            {school.name}
          </h2>
          <p className="mt-1 text-sm text-muted">
            {school.nickname ? `${school.nickname} · ` : ""}
            {school.city}, {school.stateCode}
          </p>
        </Link>
        <TargetButton schoolId={school.id} compact />
      </div>
      <Link to={`/schools/${school.id}`} className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
        <Stat label="Enrollment" value={people(school.enrollment)} />
        <Stat label="Admit" value={pct(school.acceptanceRate)} />
        <Stat label="Retention" value={pct(school.retentionRate)} />
        <Stat
          label={school.control === "public" ? "OOS tuition" : "Tuition"}
          value={money(school.tuitionOutOfState)}
        />
      </Link>
      <p className="mt-3 text-xs text-muted">
        {school.control === "public" ? "Public" : "Private"} · {school.setting} · Coach{" "}
        {school.coach}
      </p>
    </article>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-paper/70 px-2.5 py-2">
      <div className="text-[10px] tracking-wide text-muted uppercase">{label}</div>
      <div className="text-sm font-semibold">{value}</div>
    </div>
  );
}
