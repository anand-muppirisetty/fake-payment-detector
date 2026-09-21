import { Moon, Sun } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle color theme"
      className="grid h-9 w-9 place-items-center rounded-full border border-mist-300 dark:border-ink-600 text-ink-700 dark:text-mist-300 transition hover:border-signal-cyan hover:text-signal-cyan"
    >
      {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}
