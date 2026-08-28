import { Link, useParams } from "react-router-dom";
import { ArrowLeft, GraduationCap, MapPin, Trophy, Users } from "lucide-react";
import { getSchool } from "../data/catalog";
import { divisionLabel, money, people, pct } from "../lib/format";
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
        <Link to="/" className="mt-6 inline-block font-medium text-clay hover:underline">
          Back to programs
        </Link>
      </div>
    );
  }

  const tuitionSame = school.tuitionInState === school.tuitionOutOfState;

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
                <span className="rounded-full bg-gold/20 px-2 py-0.5 font-semibold text-gold">
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
          <Fact icon={Users} label="Undergraduate / total size" value={people(school.enrollment)} />
          <Fact icon={GraduationCap} label="Acceptance rate" value={pct(school.acceptanceRate)} />
          <Fact icon={GraduationCap} label="Retention rate" value={pct(school.retentionRate)} />
          <Fact
            icon={Trophy}
            label="NCAA tournament"
            value={
              school.ncaaTitles
                ? `${school.ncaaTitles} title${school.ncaaTitles === 1 ? "" : "s"} · ${school.ncaaAppearances} bids`
                : school.ncaaAppearances
                  ? `${school.ncaaAppearances} appearances`
                  : school.firstSeason
                    ? `First season ${school.firstSeason}`
                    : "See athletics site"
            }
          />
        </div>
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-2xl border border-line bg-card p-5">
          <h2 className="display text-2xl">Academics & cost</h2>
          <dl className="mt-4 divide-y divide-line text-sm">
            <Row label="School type" value={`${capitalize(school.control)} · ${school.setting}`} />
            <Row label="Enrollment" value={school.enrollment.toLocaleString()} />
            <Row label="Acceptance rate" value={pct(school.acceptanceRate)} />
            <Row label="First-year retention" value={pct(school.retentionRate)} />
            <Row
              label="SAT mid-range"
              value={school.satMid ? String(school.satMid) : "Not listed"}
            />
            <Row label="ACT mid-range" value={school.actMid ? String(school.actMid) : "Not listed"} />
            <Row
              label={tuitionSame ? "Tuition" : "In-state tuition"}
              value={money(school.tuitionInState)}
            />
            {!tuitionSame && (
              <Row label="Out-of-state tuition" value={money(school.tuitionOutOfState)} />
            )}
          </dl>
          <p className="mt-4 text-xs leading-relaxed text-muted">
            Academic figures are approximate published ranges for recruiting fit — confirm on the
            school's admissions site before you apply.
          </p>
        </section>

        <section className="rounded-2xl border border-line bg-card p-5">
          <h2 className="display text-2xl">Program</h2>
          <dl className="mt-4 divide-y divide-line text-sm">
            <Row label="Division" value={`NCAA Division ${school.division}`} />
            <Row label="Conference" value={school.conference} />
            <Row label="Head coach" value={school.coach} />
            <Row
              label="First season"
              value={school.firstSeason ? String(school.firstSeason) : "Not listed"}
            />
            <Row label="NCAA appearances" value={String(school.ncaaAppearances)} />
            <Row label="NCAA titles" value={String(school.ncaaTitles)} />
            <Row label="Region" value={`${school.region} · ${school.city}, ${school.stateCode}`} />
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

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-2.5">
      <dt className="text-muted">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}

function capitalize(value: string) {
  return value.slice(0, 1).toUpperCase() + value.slice(1);
}
