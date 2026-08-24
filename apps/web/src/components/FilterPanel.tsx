"use client";

import { theme } from "@/lib/theme";

// Control compacto de filtros reutilizable (ROADMAP §07 — "Filtros",
// "Consistencia transversal"; UI-UX-STANDARDS §11-14). Reemplaza la
// exposición permanente de selects sueltos por un botón con badge que
// abre una superficie dedicada (bottom sheet). Extraído del listado de
// OT para no duplicar la misma lógica de popover en cada módulo.

export function FilterButton({ activeCount, onClick }: { activeCount: number; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{ padding: "0.625rem 1rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", background: activeCount ? theme.primary : theme.surface, color: activeCount ? theme.primaryText : theme.text, cursor: "pointer", fontSize: "0.9375rem", fontWeight: 500 }}
    >
      Filtros{activeCount ? ` ${activeCount}` : ""}
    </button>
  );
}

export function FilterChips({
  chips,
  onRemove,
  onClearAll,
}: {
  chips: { key: string; label: string }[];
  onRemove: (key: string) => void;
  onClearAll: () => void;
}) {
  if (chips.length === 0) return null;
  return (
    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
      {chips.map((chip) => (
        <span key={chip.key} style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", background: theme.bg, border: `1px solid ${theme.border}`, borderRadius: "9999px", padding: "0.25rem 0.5rem 0.25rem 0.75rem", fontSize: "0.8125rem", color: theme.text }}>
          {chip.label}
          <button onClick={() => onRemove(chip.key)} aria-label={`Quitar filtro ${chip.label}`} style={{ background: "transparent", border: "none", cursor: "pointer", color: theme.textSecondary, fontSize: "0.9375rem", lineHeight: 1, padding: "0.125rem" }}>×</button>
        </span>
      ))}
      <button onClick={onClearAll} style={{ background: "transparent", border: "none", color: theme.primary, cursor: "pointer", fontSize: "0.8125rem", textDecoration: "underline" }}>
        Limpiar todos
      </button>
    </div>
  );
}

export function FilterPanel({
  open,
  onClose,
  onApply,
  onClear,
  children,
}: {
  open: boolean;
  onClose: () => void;
  onApply: () => void;
  onClear: () => void;
  children: React.ReactNode;
}) {
  if (!open) return null;
  return (
    <>
      <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)", zIndex: 30 }} />
      <div className="filter-panel" style={{ background: theme.surface, color: theme.text, padding: "1.25rem", maxHeight: "80vh", overflowY: "auto" }}>
        <h3 style={{ marginBottom: "1rem" }}>Filtros</h3>
        <div style={{ display: "grid", gap: "0.875rem" }}>
          {children}
        </div>
        <div style={{ display: "flex", gap: "0.5rem", marginTop: "1.25rem" }}>
          <button onClick={onApply} style={{ flex: 1, padding: "0.75rem", background: theme.primary, color: theme.primaryText, border: "none", borderRadius: "0.5rem", fontWeight: 600, cursor: "pointer" }}>
            Aplicar
          </button>
          <button onClick={onClear} style={{ padding: "0.75rem 1rem", background: "transparent", border: `1px solid ${theme.border}`, color: theme.text, borderRadius: "0.5rem", cursor: "pointer" }}>
            Limpiar
          </button>
        </div>
      </div>
    </>
  );
}
