"use client";

import { useEffect, useState } from "react";
import { theme } from "@/lib/theme";

type ThemeChoice = "light" | "dark" | "system";

function applyTheme(choice: ThemeChoice) {
  const root = document.documentElement;
  if (choice === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", choice);
}

// Toggle manual de tema claro/oscuro (ROADMAP §07 — "Tema claro/oscuro").
// Hasta ahora la app solo seguía prefers-color-scheme del sistema, sin
// forma de elegir manualmente. Guarda la preferencia en localStorage;
// el script inline en layout.tsx aplica el valor guardado antes del
// primer pintado para evitar parpadeo.
export function ThemeToggle() {
  const [choice, setChoice] = useState<ThemeChoice>("system");

  useEffect(() => {
    try {
      const saved = localStorage.getItem("gi-ot-theme") as ThemeChoice | null;
      if (saved) setChoice(saved);
    } catch {
      // localStorage puede no estar disponible (modo privado); queda en "system".
    }
  }, []);

  function cycle() {
    const next: ThemeChoice = choice === "system" ? "light" : choice === "light" ? "dark" : "system";
    setChoice(next);
    applyTheme(next);
    try { localStorage.setItem("gi-ot-theme", next); } catch { /* ignorar */ }
  }

  const icon = choice === "light" ? "☀️" : choice === "dark" ? "🌙" : "🖥️";
  const label = choice === "light" ? "Tema: claro" : choice === "dark" ? "Tema: oscuro" : "Tema: automático";

  return (
    <button
      onClick={cycle}
      aria-label={`${label}. Tocar para cambiar.`}
      title={label}
      style={{ padding: "0.375rem 0.625rem", background: "transparent", border: `1px solid ${theme.headerActive}`, color: theme.headerText, borderRadius: "0.375rem", cursor: "pointer", fontSize: "0.9375rem", lineHeight: 1 }}
    >
      {icon}
    </button>
  );
}
