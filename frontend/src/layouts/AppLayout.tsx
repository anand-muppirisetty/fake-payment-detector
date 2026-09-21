import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { LayoutDashboard, ScanSearch, History, LogOut, ShieldCheck, UploadCloud } from "lucide-react";
import ThemeToggle from "../components/common/ThemeToggle";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/upload", label: "Analyze Screenshot", icon: UploadCloud },
  { to: "/history", label: "History", icon: History },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-mist-100 dark:bg-ink-950">
      <div className="flex">
        <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col justify-between border-r border-mist-300/60 dark:border-ink-700/60 bg-white/60 dark:bg-ink-900/60 p-6 md:flex">
          <div>
            <div className="mb-10 flex items-center gap-2">
              <ScanSearch className="text-signal-cyan" size={22} />
              <span className="font-display text-lg font-bold">Fake Payment Detector AI</span>
            </div>
            <nav className="flex flex-col gap-1">
              {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                      isActive
                        ? "bg-signal-cyan/10 text-signal-cyan"
                        : "text-ink-700 hover:bg-mist-200 dark:text-mist-300 dark:hover:bg-ink-800"
                    }`
                  }
                >
                  <Icon size={17} />
                  {label}
                </NavLink>
              ))}
              {user?.role === "admin" && (
                <NavLink
                  to="/admin"
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                      isActive
                        ? "bg-signal-cyan/10 text-signal-cyan"
                        : "text-ink-700 hover:bg-mist-200 dark:text-mist-300 dark:hover:bg-ink-800"
                    }`
                  }
                >
                  <ShieldCheck size={17} />
                  Admin
                </NavLink>
              )}
            </nav>
          </div>
          <div>
            <div className="mb-3 rounded-xl bg-mist-200/70 dark:bg-ink-800/70 px-4 py-3">
              <p className="truncate text-sm font-semibold">{user?.full_name}</p>
              <p className="truncate font-mono text-xs text-ink-700/70 dark:text-mist-400">{user?.email}</p>
            </div>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="flex w-full items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium text-signal-red transition hover:bg-signal-red/10"
            >
              <LogOut size={16} /> Sign out
            </button>
          </div>
        </aside>

        <div className="min-h-screen flex-1">
          <header className="flex items-center justify-between border-b border-mist-300/60 dark:border-ink-700/60 bg-white/60 dark:bg-ink-900/60 px-6 py-4 md:hidden">
            <span className="font-display font-bold">Fake Payment Detector AI</span>
            <ThemeToggle />
          </header>
          <div className="hidden justify-end px-8 pt-6 md:flex">
            <ThemeToggle />
          </div>
          <motion.main
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="p-6 md:p-8"
          >
            <Outlet />
          </motion.main>
        </div>
      </div>
    </div>
  );
}
