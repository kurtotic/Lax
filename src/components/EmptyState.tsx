import { SearchX, SlidersHorizontal } from "lucide-react";

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: { label: string; onClick: () => void };
}) {
  return (
    <div className="rounded-2xl border border-dashed border-line bg-card/60 px-6 py-14 text-center">
      <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-full bg-paper text-moss">
        <SearchX className="h-6 w-6" />
      </div>
      <h2 className="display text-2xl">{title}</h2>
      <p className="mx-auto mt-2 max-w-md text-sm text-muted">{body}</p>
      {action && (
        <button
          type="button"
          onClick={action.onClick}
          className="mt-5 inline-flex items-center gap-2 rounded-full bg-field px-4 py-2 text-sm font-medium text-paper"
        >
          <SlidersHorizontal className="h-4 w-4" />
          {action.label}
        </button>
      )}
    </div>
  );
}
