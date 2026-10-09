import { NavLink } from "react-router-dom";
import { useRecruiting } from "../context/RecruitingStore";

export function Header() {
  const { targetIds, notesBySchool } = useRecruiting();
  const noteCount = Object.values(notesBySchool).reduce((total, notes) => total + notes.length, 0);

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-field text-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <NavLink to="/" className="display text-2xl leading-none tracking-tight">
          Lax
        </NavLink>
        <nav className="flex items-center gap-1 text-sm">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `rounded-full px-3 py-1.5 font-medium ${isActive ? "bg-white/15 text-white" : "text-white/75 hover:text-white"}`
            }
          >
            Programs
          </NavLink>
          <NavLink
            to="/notes"
            className={({ isActive }) =>
              `rounded-full px-3 py-1.5 font-medium ${isActive ? "bg-white/15 text-white" : "text-white/75 hover:text-white"}`
            }
          >
            Notes
            {noteCount > 0 && (
              <span className="ml-1.5 inline-grid h-5 min-w-5 place-items-center rounded-full bg-white px-1.5 text-[11px] font-semibold text-field">
                {noteCount}
              </span>
            )}
          </NavLink>
          <NavLink
            to="/targets"
            className={({ isActive }) =>
              `rounded-full px-3 py-1.5 font-medium ${isActive ? "bg-white/15 text-white" : "text-white/75 hover:text-white"}`
            }
          >
            Targets
            {targetIds.length > 0 && (
              <span className="ml-1.5 inline-grid h-5 min-w-5 place-items-center rounded-full bg-white px-1.5 text-[11px] font-semibold text-field">
                {targetIds.length}
              </span>
            )}
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
