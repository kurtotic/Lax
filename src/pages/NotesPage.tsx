import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Clock3, Trash2 } from "lucide-react";
import { schools } from "../data/catalog";
import { useRecruiting } from "../context/RecruitingStore";
import { formatTimestamp, relativeTime } from "../lib/format";
import { EmptyState } from "../components/EmptyState";

function localDay(iso: string): string {
  const date = new Date(iso);
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

export function NotesPage() {
  const { notesBySchool, deleteNote } = useRecruiting();
  const [schoolId, setSchoolId] = useState("");
  const [date, setDate] = useState("");

  const rows = useMemo(() => {
    return Object.entries(notesBySchool)
      .flatMap(([id, notes]) => notes.map((note) => ({ schoolId: id, note })))
      .sort((a, b) => b.note.createdAt.localeCompare(a.note.createdAt));
  }, [notesBySchool]);

  const visible = rows.filter((row) => {
    if (schoolId && row.schoolId !== schoolId) return false;
    if (date && localDay(row.note.createdAt) !== date) return false;
    return true;
  });

  const schoolName = (id: string) => schools.find((school) => school.id === id)?.name ?? id;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <p className="text-xs tracking-[0.22em] text-moss uppercase">Comments</p>
      <h1 className="display mt-1 text-4xl">Notes</h1>
      <p className="mt-2 max-w-xl text-sm text-muted">
        Every comment, newest first. Filter by school or by the day it was written. Notes stay in
        this browser.
      </p>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <label className="text-sm">
          <span className="mb-1 block text-muted">School</span>
          <select
            value={schoolId}
            onChange={(event) => setSchoolId(event.target.value)}
            className="w-full rounded-xl border border-line bg-white px-3 py-2"
          >
            <option value="">All schools</option>
            {schools.map((school) => (
              <option key={school.id} value={school.id}>
                {school.name}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-muted">Date</span>
          <input
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
            className="w-full rounded-xl border border-line bg-white px-3 py-2"
          />
        </label>
      </div>

      <p className="mt-4 text-sm text-muted">
        <span className="font-semibold text-ink">{visible.length}</span>
        {visible.length === rows.length ? " notes" : ` of ${rows.length} notes`}
      </p>

      {rows.length === 0 ? (
        <div className="mt-6">
          <EmptyState
            title="No notes yet"
            body="Open a school and save a comment. It will show up here, newest first."
          />
        </div>
      ) : visible.length === 0 ? (
        <div className="mt-6">
          <EmptyState
            title="No notes match"
            body="Try another school or date, or clear the filters to see every comment."
            action={{
              label: "Clear filters",
              onClick: () => {
                setSchoolId("");
                setDate("");
              },
            }}
          />
        </div>
      ) : (
        <ol className="mt-4 space-y-3">
          {visible.map((row) => (
            <li key={row.note.id} className="rounded-2xl border border-line bg-white p-4">
              <div className="mb-2 flex items-start justify-between gap-3">
                <div>
                  <Link
                    to={`/schools/${row.schoolId}`}
                    className="display text-xl hover:underline"
                  >
                    {schoolName(row.schoolId)}
                  </Link>
                  <p
                    className="mt-0.5 inline-flex items-center gap-1.5 text-xs text-muted"
                    title={formatTimestamp(row.note.createdAt)}
                  >
                    <Clock3 className="h-3.5 w-3.5" />
                    <span>{relativeTime(row.note.createdAt)}</span>
                    <span>· {formatTimestamp(row.note.createdAt)}</span>
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => deleteNote(row.schoolId, row.note.id)}
                  className="rounded-full p-1 text-muted hover:bg-line/70 hover:text-ink"
                  aria-label="Delete note"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{row.note.text}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
