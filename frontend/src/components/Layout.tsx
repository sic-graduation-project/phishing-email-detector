import { NavLink, Outlet } from "react-router-dom";
import {
  ShieldCheck,
  Home,
  History,
  Settings,
  HelpCircle,
  Moon,
  Sun,
  ChevronDown,
} from "lucide-react";
import { useTheme } from "../hooks/useTheme";
import NotificationsDropdown from "./NotificationsDropdown";

const navItems = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/history", label: "Analysis History", icon: History, end: false },
  { to: "/settings", label: "Settings", icon: Settings, end: false },
  { to: "/help", label: "Help & Support", icon: HelpCircle, end: false },
];

export default function Layout() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen flex flex-col bg-[#f4f7fc] dark:bg-[#0b0f1a]">
      <header className="sticky top-0 z-30 border-b border-slate-200 dark:border-white/10 bg-white dark:bg-[#0f1420] px-4 sm:px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div aria-label="Nexus" className="grid place-items-center h-10 w-10 rounded-xl bg-blue-600 text-white shadow-md shadow-blue-600/20">
            <ShieldCheck size={22} />
          </div>
          <div className="leading-tight">
            <p className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">
              Nexus
            </p>
            <p className="text-[11px] text-slate-400 dark:text-slate-500">
              Detect. Protect. Stay Safe.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          <button
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
            className="grid place-items-center h-9 w-9 rounded-full text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          <NotificationsDropdown />

          <div className="flex items-center gap-2 pl-2 sm:border-l border-slate-200 dark:border-white/10">
            <div className="grid place-items-center h-8 w-8 rounded-full bg-blue-600 text-white text-sm font-semibold">
              G
            </div>
            <span className="hidden sm:inline text-sm text-slate-600 dark:text-slate-300">
              Hello, Guest
            </span>
            <ChevronDown size={14} className="hidden sm:inline text-slate-400" />
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        <aside className="hidden md:flex w-60 shrink-0 flex-col border-r border-slate-200 dark:border-white/10 bg-white dark:bg-[#0f1420] px-3 py-5">
          <nav className="flex flex-col gap-1">
            {navItems.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400"
                      : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-slate-800 dark:hover:text-white"
                  }`
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto pt-6">
            <div className="rounded-2xl bg-gradient-to-b from-blue-50 to-blue-100/60 dark:from-blue-500/10 dark:to-blue-500/5 p-5 text-center">
              <div className="mx-auto grid place-items-center h-14 w-14 rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/30">
                <ShieldCheck size={26} />
              </div>
              <p className="mt-3 font-bold text-slate-900 dark:text-white leading-tight">
                Stay Aware
                <br />
                Stay Secure
              </p>
              <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">
                AI-powered protection for a safer digital world.
              </p>
            </div>
          </div>
        </aside>

        <main className="flex-1 min-w-0 px-4 sm:px-8 py-8">
          <Outlet />
        </main>
      </div>

      <footer className="border-t border-slate-200 dark:border-white/10 bg-white dark:bg-[#0f1420] px-4 sm:px-8 py-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-400">
        <span>© 2026 PhishGuard. All rights reserved.</span>
        <div className="flex items-center gap-4">
          <span>Privacy</span>
          <span>Terms</span>
          <span>Contact</span>
        </div>
      </footer>
    </div>
  );
}
