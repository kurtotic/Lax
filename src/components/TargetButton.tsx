import { Flag, FlagOff } from "lucide-react";
import { useRecruiting } from "../context/RecruitingStore";

export function TargetButton({
  schoolId,
  compact = false,
}: {
  schoolId: string;
  compact?: boolean;
}) {
  const { isTarget, toggleTarget, targetRank } = useRecruiting();
  const on = isTarget(schoolId);
  const rank = targetRank(schoolId);

  return (
    <button
      type="button"
      onClick={(event) => {
        event.preventDefault();
        event.stopPropagation();
        toggleTarget(schoolId);
      }}
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-medium transition ${
        on
          ? "border-clay/30 bg-clay text-white shadow-sm"
          : "border-line bg-card text-ink hover:border-clay/40 hover:text-clay"
      }`}
      aria-pressed={on}
    >
      {on ? <Flag className="h-3.5 w-3.5" /> : <FlagOff className="h-3.5 w-3.5" />}
      {compact ? (
        on ? `Target #${rank}` : "Target"
      ) : on ? (
        `On list · #${rank}`
      ) : (
        "Add to targets"
      )}
    </button>
  );
}
