"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { theme } from "@/lib/theme";
import { CurrentUser, WorkOrder } from "@/lib/types";
import { StatusBadge, PriorityBadge } from "@/components/StatusPriorityBadge";

export default function MisOTPage() {
  const [wos, setWos] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true); setError(null);
    try {
      const me = await api.get<CurrentUser>("/auth/me");
      if (!me.technician_person_id) {
        setWos([]);
        return;
      }
      const list = await api.get<WorkOrder[]>(`/work-orders?technician_id=${me.technician_person_id}`);
      setWos(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar OT");
    } finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1 style={{ fontSize: "1.25rem", color: theme.text }}>Mis OT</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link
            href="/tecnico/qr"
            style={{ padding: "0.5rem 0.875rem", background: theme.bg, color: theme.text, borderRadius: "0.5rem", textDecoration: "none", fontSize: "0.875rem", fontWeight: 600 }}
          >
            📷 QR
          </Link>
          <Link
            href="/tecnico/nueva"
            style={{ padding: "0.5rem 0.875rem", background: theme.dangerSolid, color: theme.primaryText, borderRadius: "0.5rem", textDecoration: "none", fontSize: "0.875rem", fontWeight: 600 }}
          >
            + OT urgente
          </Link>
        </div>
      </div>

      {error && (
        <div style={{ background: theme.dangerBg, border: `1px solid ${theme.border}`, color: theme.danger, padding: "0.75rem", borderRadius: "0.5rem", marginBottom: "1rem", fontSize: "0.875rem" }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>Cargando...</div>
      ) : wos.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>No tenés OT asignadas.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {wos.map((wo) => (
            <Link
              key={wo.id}
              href={`/tecnico/ot/${wo.id}`}
              style={{ display: "block", background: theme.surface, border: `1px solid ${theme.border}`, borderRadius: "0.75rem", padding: "1rem", textDecoration: "none", color: "inherit" }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                <span style={{ fontWeight: 600, color: theme.text }}>OT #{wo.number}</span>
                <PriorityBadge code={wo.priority_code} label={wo.priority_label} />
              </div>
              <div style={{ fontSize: "0.875rem", color: theme.textSecondary, marginTop: "0.25rem" }}>{wo.requested_description}</div>
              <div style={{ marginTop: "0.375rem" }}>
                <StatusBadge code={wo.status_code} label={wo.status_label} />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
