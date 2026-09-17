"use client";

import { theme } from "@/lib/theme";

// Estado de error con recuperación (ROADMAP §07 — "Estados de interfaz").
// onRetry es opcional: los errores de envío de formulario (el usuario ya
// tiene el botón de submit para reintentar) no necesitan uno; los errores
// de carga de datos sí.
export function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", background: theme.dangerBg, color: theme.danger, padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>
      <span>{message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{ flexShrink: 0, padding: "0.375rem 0.875rem", background: "transparent", border: `1px solid ${theme.danger}`, color: theme.danger, borderRadius: "0.375rem", cursor: "pointer", fontSize: "0.8125rem", fontWeight: 600 }}
        >
          Reintentar
        </button>
      )}
    </div>
  );
}
