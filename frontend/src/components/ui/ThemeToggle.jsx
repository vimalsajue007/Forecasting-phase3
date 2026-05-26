import { useTheme } from "../../hooks/useTheme";
import { MdLightMode, MdDarkMode } from "react-icons/md";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-xl transition-all duration-200 hover:bg-primary-100 dark:hover:bg-primary-900"
      title={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
    >
      {theme === "light" ? (
        <MdDarkMode className="text-xl text-primary-600" />
      ) : (
        <MdLightMode className="text-xl text-yellow-400" />
      )}
    </button>
  );
}
