import { theme } from "@/lib/theme";

// Estados y prioridades parametrizadas (ROADMAP §07, UI-UX-STANDARDS §22):
// el componente mapea por `code` (semántica interna estable), nunca por
// `label` (etiqueta visible configurable por tenant) — así la app no
// asume nombres, cantidades ni colores fijos definidos por el tenant.
const STATUS_TOKENS: Record<string, { bg: string; fg: string }> = {
  PENDING: { bg: theme.successBg, fg: theme.success },
  IN_PROGRESS: { bg: theme.warningBg, fg: theme.warning },
  COMPLETED: { bg: theme.successBg, fg: theme.success },
  UNRESOLVED: { bg: theme.dangerBg, fg: theme.danger },
};

const badgeStyle = {
  padding: "0.1875rem 0.625rem",
  borderRadius: "9999px",
  fontSize: "0.75rem",
  fontWeight: 600,
  display: "inline-block",
} as const;

export function StatusBadge({ code, label }: { code: string; label?: string | null }) {
  const color = STATUS_TOKENS[code] || { bg: theme.bg, fg: theme.textSecondary };
  return <span style={{ ...badgeStyle, background: color.bg, color: color.fg }}>{label || code}</span>;
}

// Solo URGENT se destaca visualmente hoy — el resto de las prioridades
// (LOW/NORMAL/HIGH) no necesitan llamar la atención en un listado.
export function PriorityBadge({ code, label }: { code: string | null; label?: string | null }) {
  if (code !== "URGENT") return null;
  return <span style={{ ...badgeStyle, fontWeight: 700, background: theme.dangerBg, color: theme.danger }}>{label || "Urgente"}</span>;
}
