import { NavLink } from "react-router-dom";
import { useRecruiting } from "../context/RecruitingStore";

export function Header() {
  const { targetIds } = useRecruiting();

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-field/95 text-paper backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <NavLink to="/" className="group flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-gold text-field shadow-sm">
            <svg viewBox="0 0 32 32" className="h-6 w-6" aria-hidden>
              <path
                d="M9 24.5c4.2-7.4 7.8-14.2 14-18"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
              />
              <path
                d="M21.2 6.2c2.4 1.1 3.8 3.6 2.6 6.2-1.4 3-5.2 3.2-6.8.8-1.2-1.8-.4-4.2 1.6-5.2"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </span>
          <span>
            <span className="display block text-lg leading-none font-semibold tracking-tight">
              Lax
            </span>
            <span className="text-[11px] tracking-[0.18em] text-paper/70 uppercase">
              Women's recruiting
            </span>
          </span>
        </NavLink>
        <nav className="flex items-center gap-1 text-sm">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `rounded-full px-3 py-1.5 font-medium ${isActive ? "bg-white/12 text-white" : "text-paper/75 hover:text-white"}`
            }
          >
            Programs
          </NavLink>
          <NavLink
            to="/targets"
            className={({ isActive }) =>
              `rounded-full px-3 py-1.5 font-medium ${isActive ? "bg-white/12 text-white" : "text-paper/75 hover:text-white"}`
            }
          >
            Targets
            {targetIds.length > 0 && (
              <span className="ml-1.5 inline-grid h-5 min-w-5 place-items-center rounded-full bg-gold px-1.5 text-[11px] font-semibold text-field">
                {targetIds.length}
              </span>
            )}
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
