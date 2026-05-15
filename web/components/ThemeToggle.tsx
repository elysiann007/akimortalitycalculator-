"use client";

import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

interface Props {
  className?: string;
  style?: React.CSSProperties;
}

export default function ThemeToggle({ className, style }: Props) {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const stored = localStorage.getItem("aki-theme");
    const initial = stored === "light" ? "light" : "dark";
    setTheme(initial);
    document.documentElement.setAttribute("data-theme", initial);
  }, []);

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("aki-theme", next);
  };

  return (
    <button
      onClick={toggle}
      className={className}
      style={style}
      title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
    >
      {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </button>
  );
}
