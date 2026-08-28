import type { Note, PersistedState } from "../types";

const KEY = "lax-recruiting-v1";

const empty: PersistedState = {
  notesBySchool: {},
  targetIds: [],
};

export function loadState(): PersistedState {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return empty;
    const parsed = JSON.parse(raw) as Partial<PersistedState>;
    return {
      notesBySchool: parsed.notesBySchool ?? {},
      targetIds: Array.isArray(parsed.targetIds) ? parsed.targetIds : [],
    };
  } catch {
    return empty;
  }
}

export function saveState(state: PersistedState): void {
  localStorage.setItem(KEY, JSON.stringify(state));
}

export function createNote(text: string): Note {
  return {
    id: crypto.randomUUID(),
    text: text.trim(),
    createdAt: new Date().toISOString(),
  };
}
