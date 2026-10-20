import type { ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, GraduationCap, MapPin, Users } from "lucide-react";
import { getSchool } from "../data/catalog";
import { divisionLabel, listed, money, people, pct } from "../lib/format";
import { NotesTimeline } from "../components/NotesTimeline";
import { TargetButton } from "../components/TargetButton";

export function SchoolPage() {
  const { id } = useParams();
  const school = id ? getSchool(id) : undefined;

  if (!school) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <h1 className="display text-3xl">School not found</h1>
        <p className="mt-2 text-muted">That program is not in the catalog.</p>
        <Link to="/" className="mt-6 inline-block font-medium text-field hover:underline">
          Back to programs
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link
        to="/"
        className="mb-5 inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" />
        All programs
      </Link>

      <section className="overflow-hidden rounded-3xl border border-line bg-card">
        <div className="bg-field px-5 py-7 text-paper sm:px-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
                <span className="rounded-full bg-white/15 px-2 py-0.5 font-semibold text-white">
                  {divisionLabel(school.division)} women's lacrosse
                </span>
                <span className="text-paper/70">{school.conference}</span>
              </div>
              <h1 className="display text-4xl leading-tight sm:text-5xl">{school.name}</h1>
              <p className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-paper/80">
                {school.nickname && <span>{school.nickname}</span>}
                <span className="inline-flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {school.city}, {school.state}
                </span>
              </p>
            </div>
            <TargetButton schoolId={school.id} />
          </div>
        </div>

        <div className="grid gap-3 p-5 sm:grid-cols-2 sm:p-8 lg:grid-cols-4">
          <Fact icon={Users} label="Undergraduate enrollment" value={people(school.enrollment)} />
          <Fact icon={GraduationCap} label="Acceptance rate" value={pct(school.acceptanceRate)} />
          <Fact icon={GraduationCap} label="Retention rate" value={pct(school.retentionRate)} />
          <Fact icon={GraduationCap} label="Graduation rate" value={pct(school.graduationRate)} />
        </div>
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-2xl border border-line bg-card p-5">
          <h2 className="display text-2xl">Academics & cost</h2>
          <dl className="mt-4 divide-y divide-line text-sm">
            <Row
              label="School type"
              value={school.control ? capitalize(school.control) : "Not listed"}
            />
            <Row label="Enrollment" value={people(school.enrollment)} />
            <Row label="Acceptance rate" value={pct(school.acceptanceRate)} />
            <Row label="First-year retention" value={pct(school.retentionRate)} />
            <Row label="Graduation rate" value={pct(school.graduationRate)} />
            <Row label="SAT range" value={listed(school.satRange)} />
            <Row label="SAT mean" value={school.satMean == null ? "Not listed" : String(school.satMean)} />
            <Row label="Test policy" value={listed(school.testPolicy)} />
            <Row label="Tuition" value={money(school.tuitionOutOfState)} />
          </dl>
          <p className="mt-4 text-xs leading-relaxed text-muted">
            Figures come from the recruiting sheet. Not listed means that cell was empty — nothing
            here is estimated. Confirm stats with the school before you apply.
          </p>
        </section>

        <section className="rounded-2xl border border-line bg-card p-5">
          <h2 className="display text-2xl">Program</h2>
          <dl className="mt-4 divide-y divide-line text-sm">
            <Row label="Division" value={`NCAA Division ${school.division}`} />
            <Row label="Conference" value={school.conference} />
            <Row label="Head coach" value={listed(school.coach)} />
            <Row label="Coach email" value={<EmailValue value={school.coachEmail} />} />
            <Row label="Region" value={school.region ? `${school.region} · ${school.city}, ${school.stateCode}` : `${school.city}, ${school.stateCode}`} />
          </dl>
        </section>
      </div>

      <div className="mt-6">
        <NotesTimeline schoolId={school.id} schoolName={school.name} />
      </div>
    </div>
  );
}

function Fact({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Users;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl bg-paper/80 p-3">
      <div className="mb-2 text-moss">
        <Icon className="h-4 w-4" />
      </div>
      <div className="text-[11px] tracking-wide text-muted uppercase">{label}</div>
      <div className="mt-0.5 font-semibold">{value}</div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-2.5">
      <dt className="text-muted">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}

function EmailValue({ value }: { value: string }) {
  const text = value.trim();
  if (!text) return "Not listed";
  const match = text.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
  if (!match) return text;
  const email = match[0];
  const note = text.replace(email, "").trim();
  return (
    <>
      <a className="underline" href={`mailto:${email}`}>
        {email}
      </a>
      {note ? ` ${note}` : null}
    </>
  );
}

function capitalize(value: string) {
  return value.slice(0, 1).toUpperCase() + value.slice(1);
}
