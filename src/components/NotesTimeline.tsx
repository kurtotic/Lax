import { useState, type FormEvent } from "react";
import { Clock3, Trash2 } from "lucide-react";
import { useRecruiting } from "../context/RecruitingStore";
import { formatTimestamp, relativeTime } from "../lib/format";

export function NotesTimeline({ schoolId, schoolName }: { schoolId: string; schoolName: string }) {
  const { notesFor, addNote, deleteNote } = useRecruiting();
  const [text, setText] = useState("");
  const notes = notesFor(schoolId);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    addNote(schoolId, text);
    setText("");
  };

  return (
    <section className="rounded-2xl border border-line bg-card p-5">
      <div className="mb-4">
        <h2 className="display text-2xl">Notes</h2>
        <p className="text-sm text-muted">
          A private timeline for {schoolName}. Saved on this device.
        </p>
      </div>
      <form onSubmit={onSubmit} className="mb-6">
        <label htmlFor="note" className="mb-1.5 block text-sm font-medium">
          Add a note
        </label>
        <textarea
          id="note"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder={`Emailed ${schoolName} coach with file and tournament schedule.`}
          rows={3}
          className="w-full resize-y rounded-xl border border-line bg-white px-3 py-2 text-sm outline-none ring-field/20 focus:ring-4"
        />
        <div className="mt-2 flex items-center justify-between gap-3">
          <p className="text-xs text-muted">Date and time are stored with every note.</p>
          <button
            type="submit"
            disabled={!text.trim()}
            className="rounded-full bg-field px-4 py-2 text-sm font-semibold text-paper disabled:opacity-40"
          >
            Save note
          </button>
        </div>
      </form>
      {notes.length === 0 ? (
        <p className="rounded-xl bg-field/5 px-4 py-6 text-center text-sm text-muted">
          No notes yet. Track emails, camps, visits, and follow-ups here.
        </p>
      ) : (
        <ol className="relative space-y-4 border-l border-line pl-4">
          {notes.map((note) => (
            <li key={note.id} className="relative">
              <span className="absolute top-1.5 -left-[21px] h-2.5 w-2.5 rounded-full bg-field ring-4 ring-card" />
              <div className="rounded-xl bg-field/5 px-3 py-3">
                <div className="mb-1 flex items-start justify-between gap-3">
                  <p
                    className="inline-flex items-center gap-1.5 text-xs text-muted"
                    title={formatTimestamp(note.createdAt)}
                  >
                    <Clock3 className="h-3.5 w-3.5" />
                    <span>{relativeTime(note.createdAt)}</span>
                    <span className="hidden sm:inline">· {formatTimestamp(note.createdAt)}</span>
                  </p>
                  <button
                    type="button"
                    onClick={() => deleteNote(schoolId, note.id)}
                    className="rounded-full p-1 text-muted hover:bg-line/70 hover:text-field"
                    aria-label="Delete note"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{note.text}</p>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
