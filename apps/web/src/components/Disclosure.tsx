"use client";

import { useState } from "react";
import { theme } from "@/lib/theme";

// Revelado progresivo (ROADMAP §07 — "Aplicar revelado progresivo a
// opciones avanzadas cuando corresponda"; UI-UX-STANDARDS §5). Oculta
// campos secundarios de un formulario detrás de un toggle, dejando
// visibles solo los datos imprescindibles por defecto.
export function Disclosure({ label, children }: { label: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ marginBottom: "1.5rem" }}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        style={{ display: "flex", alignItems: "center", gap: "0.375rem", background: "transparent", border: "none", color: theme.primary, cursor: "pointer", fontSize: "0.9375rem", fontWeight: 500, padding: 0, marginBottom: open ? "1rem" : 0 }}
      >
        <span style={{ display: "inline-block", transform: open ? "rotate(90deg)" : "none", transition: "transform 0.15s" }}>›</span>
        {open ? `Ocultar ${label.toLowerCase()}` : label}
      </button>
      {open && <div style={{ display: "grid", gap: "1rem" }}>{children}</div>}
    </div>
  );
}
