"use client";

import { useState } from "react";
import { theme } from "@/lib/theme";

// Control compacto de ordenamiento reutilizable (ROADMAP §07 —
// "Ordenamiento", "Consistencia transversal"; UI-UX-STANDARDS §15).
// Extraído del listado de OT para que todos los módulos usen el mismo
// patrón en vez de reinventar un dropdown por pantalla.
export function SortButton<T extends string>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
}) {
  const [open, setOpen] = useState(false);
  const current = options.find((o) => o.value === value);

  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={() => setOpen((v) => !v)}
        style={{ padding: "0.625rem 1rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", background: theme.surface, color: theme.text, cursor: "pointer", fontSize: "0.9375rem", fontWeight: 500 }}
      >
        Ordenar: {current?.label}
      </button>
      {open && (
        <>
          <div onClick={() => setOpen(false)} style={{ position: "fixed", inset: 0, zIndex: 20 }} />
          <div style={{ position: "absolute", right: 0, top: "calc(100% + 0.25rem)", background: theme.surface, border: `1px solid ${theme.border}`, borderRadius: "0.5rem", boxShadow: "0 4px 16px rgba(0,0,0,0.15)", zIndex: 21, minWidth: "200px", overflow: "hidden" }}>
            {options.map((opt) => (
              <button
                key={opt.value}
                onClick={() => { onChange(opt.value); setOpen(false); }}
                style={{ display: "block", width: "100%", textAlign: "left", padding: "0.625rem 0.875rem", background: opt.value === value ? theme.bg : "transparent", border: "none", color: theme.text, cursor: "pointer", fontSize: "0.875rem" }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
