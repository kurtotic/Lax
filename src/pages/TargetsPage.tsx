import { Link } from "react-router-dom";
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { ChevronDown, ChevronUp, GripVertical, MapPin } from "lucide-react";
import { useRecruiting } from "../context/RecruitingStore";
import { getSchool } from "../data/catalog";
import { divisionLabel, money, pct } from "../lib/format";
import { EmptyState } from "../components/EmptyState";
import type { School } from "../types";

export function TargetsPage() {
  const { targetIds, setTargetOrder, moveTarget, toggleTarget } = useRecruiting();
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const ranked = targetIds
    .map((id) => getSchool(id))
    .filter((school): school is School => Boolean(school));

  const onDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = targetIds.indexOf(String(active.id));
    const newIndex = targetIds.indexOf(String(over.id));
    if (oldIndex < 0 || newIndex < 0) return;
    setTargetOrder(arrayMove(targetIds, oldIndex, newIndex));
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <p className="text-xs tracking-[0.22em] text-moss uppercase">Your board</p>
      <h1 className="display mt-1 text-4xl">Target schools</h1>
      <p className="mt-2 max-w-xl text-sm text-muted">
        Rank the programs you are actively recruiting. Drag to reorder, or use the arrows. The
        order is saved on this device.
      </p>

      {ranked.length === 0 ? (
        <div className="mt-8">
          <EmptyState
            title="No targets yet"
            body="Open a school and tap Add to targets. Build a short list you can actually work — then stack-rank it as conversations evolve."
          />
          <div className="mt-4 text-center">
            <Link
              to="/"
              className="inline-flex rounded-full bg-field px-4 py-2 text-sm font-semibold text-paper"
            >
              Browse programs
            </Link>
          </div>
        </div>
      ) : (
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
          <SortableContext items={targetIds} strategy={verticalListSortingStrategy}>
            <ol className="mt-6 space-y-3">
              {ranked.map((school, index) => (
                <SortableTarget
                  key={school.id}
                  school={school}
                  rank={index + 1}
                  isFirst={index === 0}
                  isLast={index === ranked.length - 1}
                  onMove={moveTarget}
                  onRemove={toggleTarget}
                />
              ))}
            </ol>
          </SortableContext>
        </DndContext>
      )}
    </div>
  );
}

function SortableTarget({
  school,
  rank,
  isFirst,
  isLast,
  onMove,
  onRemove,
}: {
  school: School;
  rank: number;
  isFirst: boolean;
  isLast: boolean;
  onMove: (id: string, direction: -1 | 1) => void;
  onRemove: (id: string) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: school.id,
  });

  return (
    <li
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className={`rounded-2xl border border-line bg-card p-3 shadow-sm ${isDragging ? "z-10 ring-2 ring-gold" : ""}`}
    >
      <div className="flex items-start gap-3">
        <button
          type="button"
          className="mt-1 cursor-grab touch-none rounded-lg p-1 text-muted hover:bg-paper active:cursor-grabbing"
          aria-label={`Drag to reorder ${school.name}`}
          {...attributes}
          {...listeners}
        >
          <GripVertical className="h-5 w-5" />
        </button>
        <div className="display grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-field text-lg text-gold">
          {rank}
        </div>
        <div className="min-w-0 flex-1">
          <Link to={`/schools/${school.id}`} className="display text-xl hover:text-field">
            {school.name}
          </Link>
          <p className="mt-0.5 flex flex-wrap items-center gap-x-2 text-sm text-muted">
            <span>{divisionLabel(school.division)}</span>
            <span>· {school.conference}</span>
          </p>
          <p className="mt-1 flex items-center gap-1 text-xs text-muted">
            <MapPin className="h-3.5 w-3.5" />
            {school.city}, {school.stateCode} · {pct(school.acceptanceRate)} admit ·{" "}
            {money(school.tuitionOutOfState)}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className="flex">
            <button
              type="button"
              disabled={isFirst}
              onClick={() => onMove(school.id, -1)}
              className="rounded-l-lg border border-line p-1 disabled:opacity-30"
              aria-label="Move up"
            >
              <ChevronUp className="h-4 w-4" />
            </button>
            <button
              type="button"
              disabled={isLast}
              onClick={() => onMove(school.id, 1)}
              className="rounded-r-lg border border-l-0 border-line p-1 disabled:opacity-30"
              aria-label="Move down"
            >
              <ChevronDown className="h-4 w-4" />
            </button>
          </div>
          <button
            type="button"
            onClick={() => onRemove(school.id)}
            className="text-xs font-medium text-clay hover:underline"
          >
            Remove
          </button>
        </div>
      </div>
    </li>
  );
}
