"use client";

import Link from "next/link";
import { theme } from "@/lib/theme";
import { WorkOrder } from "@/lib/types";
import { StatusBadge, PriorityBadge } from "@/components/StatusPriorityBadge";

// Historial de OT de un Cliente o de un Activo (ROADMAP §07 — "Historial
// por cliente" / "Historial por activo"): reutiliza GET /work-orders con
// el filtro correspondiente (customer_id / asset_id) y presenta los
// resultados en orden cronológico, cada uno accesible sin navegación
// adicional (UI-UX-STANDARDS §16).
export function WorkOrderHistoryList({ workOrders, emptyText }: { workOrders: WorkOrder[]; emptyText: string }) {
  if (workOrders.length === 0) {
    return <p style={{ color: theme.textSecondary, fontSize: "0.9375rem" }}>{emptyText}</p>;
  }

  const sorted = [...workOrders].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div style={{ display: "grid", gap: "0.625rem" }}>
      {sorted.map((wo) => (
        <Link key={wo.id} href={`/dashboard/ot/${wo.id}`} style={{ textDecoration: "none", color: "inherit" }}>
          <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.625rem", padding: "0.75rem 1rem", background: theme.surface }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
              <span style={{ fontWeight: 600, color: theme.text }}>OT #{wo.number}</span>
              <div style={{ display: "flex", gap: "0.375rem" }}>
                <PriorityBadge code={wo.priority_code} label={wo.priority_label} />
                <StatusBadge code={wo.status_code} label={wo.status_label} />
              </div>
            </div>
            <div style={{ fontSize: "0.8125rem", color: theme.textSecondary, marginTop: "0.25rem" }}>
              {wo.requested_description}
            </div>
            {wo.performed_description && (
              <div style={{ fontSize: "0.8125rem", color: theme.text, marginTop: "0.25rem" }}>
                Resultado: {wo.performed_description}
              </div>
            )}
            <div style={{ fontSize: "0.75rem", color: theme.textSecondary, marginTop: "0.25rem" }}>
              {new Date(wo.created_at).toLocaleDateString()}
              {wo.finished_at && ` • Finalizada ${new Date(wo.finished_at).toLocaleDateString()}`}
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
