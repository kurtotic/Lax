import { useRef } from "react";
import { useRecruiting } from "../context/RecruitingStore";
import { parseBackup } from "../lib/storage";

export function DataBackup() {
  const { notesBySchool, targetIds, replaceAll } = useRecruiting();
  const fileRef = useRef<HTMLInputElement>(null);

  const download = () => {
    const blob = new Blob([JSON.stringify({ notesBySchool, targetIds }, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "lax-recruiting-backup.json";
    link.click();
    URL.revokeObjectURL(url);
  };

  const onFile = async (file: File | undefined) => {
    if (!file) return;
    const next = parseBackup(await file.text());
    if (!next) {
      window.alert("That file does not look like a Lax backup.");
      return;
    }
    replaceAll(next);
  };

  return (
    <section className="mt-10 rounded-2xl border border-line bg-white p-5">
      <h2 className="display text-xl">Backup</h2>
      <p className="mt-1 text-sm text-muted">
        Notes and targets live in this browser only. Download a backup, then restore it on your
        iPhone, iPad, or another computer so the same list follows you.
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={download}
          className="rounded-full bg-field px-4 py-2 text-sm font-semibold text-white"
        >
          Download backup
        </button>
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          className="rounded-full border border-line px-4 py-2 text-sm font-medium"
        >
          Restore backup
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="application/json,.json"
          className="hidden"
          onChange={(event) => {
            void onFile(event.target.files?.[0]);
            event.target.value = "";
          }}
        />
      </div>
    </section>
  );
}
