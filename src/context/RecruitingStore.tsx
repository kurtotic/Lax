import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { createNote, loadState, saveState } from "../lib/storage";
import type { Note, PersistedState } from "../types";

interface StoreValue extends PersistedState {
  notesFor: (schoolId: string) => Note[];
  addNote: (schoolId: string, text: string) => void;
  deleteNote: (schoolId: string, noteId: string) => void;
  isTarget: (schoolId: string) => boolean;
  toggleTarget: (schoolId: string) => void;
  setTargetOrder: (ids: string[]) => void;
  moveTarget: (schoolId: string, direction: -1 | 1) => void;
  targetRank: (schoolId: string) => number | null;
}

const StoreContext = createContext<StoreValue | null>(null);

function persist(next: PersistedState): PersistedState {
  saveState(next);
  return next;
}

export function RecruitingProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PersistedState>(() =>
    typeof localStorage === "undefined" ? { notesBySchool: {}, targetIds: [] } : loadState(),
  );

  const notesFor = useCallback(
    (schoolId: string) => state.notesBySchool[schoolId] ?? [],
    [state.notesBySchool],
  );

  const addNote = useCallback((schoolId: string, text: string) => {
    const note = createNote(text);
    if (!note.text) return;
    setState((prev) =>
      persist({
        ...prev,
        notesBySchool: {
          ...prev.notesBySchool,
          [schoolId]: [note, ...(prev.notesBySchool[schoolId] ?? [])],
        },
      }),
    );
  }, []);

  const deleteNote = useCallback((schoolId: string, noteId: string) => {
    setState((prev) =>
      persist({
        ...prev,
        notesBySchool: {
          ...prev.notesBySchool,
          [schoolId]: (prev.notesBySchool[schoolId] ?? []).filter((n) => n.id !== noteId),
        },
      }),
    );
  }, []);

  const isTarget = useCallback(
    (schoolId: string) => state.targetIds.includes(schoolId),
    [state.targetIds],
  );

  const toggleTarget = useCallback((schoolId: string) => {
    setState((prev) => {
      const exists = prev.targetIds.includes(schoolId);
      return persist({
        ...prev,
        targetIds: exists
          ? prev.targetIds.filter((id) => id !== schoolId)
          : [...prev.targetIds, schoolId],
      });
    });
  }, []);

  const setTargetOrder = useCallback((ids: string[]) => {
    setState((prev) => persist({ ...prev, targetIds: ids }));
  }, []);

  const moveTarget = useCallback((schoolId: string, direction: -1 | 1) => {
    setState((prev) => {
      const ids = [...prev.targetIds];
      const index = ids.indexOf(schoolId);
      const next = index + direction;
      if (index < 0 || next < 0 || next >= ids.length) return prev;
      [ids[index], ids[next]] = [ids[next], ids[index]];
      return persist({ ...prev, targetIds: ids });
    });
  }, []);

  const targetRank = useCallback(
    (schoolId: string) => {
      const index = state.targetIds.indexOf(schoolId);
      return index === -1 ? null : index + 1;
    },
    [state.targetIds],
  );

  const value = useMemo<StoreValue>(
    () => ({
      ...state,
      notesFor,
      addNote,
      deleteNote,
      isTarget,
      toggleTarget,
      setTargetOrder,
      moveTarget,
      targetRank,
    }),
    [
      state,
      notesFor,
      addNote,
      deleteNote,
      isTarget,
      toggleTarget,
      setTargetOrder,
      moveTarget,
      targetRank,
    ],
  );

  return createElement(StoreContext.Provider, { value }, children);
}

export function useRecruiting() {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useRecruiting must be used within RecruitingProvider");
  return ctx;
}
