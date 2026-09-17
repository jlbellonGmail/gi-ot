"use client";

import { theme } from "@/lib/theme";

// Feedback explícito de éxito (ROADMAP §07 — "Estados de interfaz"):
// antes una edición guardada solo se reflejaba implícitamente (se
// cerraba el modo edición), sin confirmación visible.
export function SuccessBanner({ message }: { message: string }) {
  return (
    <div style={{ background: theme.successBg, color: theme.success, padding: "0.75rem 1rem", borderRadius: "0.5rem", marginBottom: "1rem", fontSize: "0.875rem" }}>
      {message}
    </div>
  );
}
