"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { CurrentUser, WorkOrder } from "@/lib/types";

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
        <h1 style={{ fontSize: "1.25rem" }}>Mis OT</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link
            href="/tecnico/qr"
            style={{ padding: "0.5rem 0.875rem", background: "#f3f4f6", color: "#374151", borderRadius: "0.5rem", textDecoration: "none", fontSize: "0.875rem", fontWeight: 600 }}
          >
            📷 QR
          </Link>
          <Link
            href="/tecnico/nueva"
            style={{ padding: "0.5rem 0.875rem", background: "#dc2626", color: "white", borderRadius: "0.5rem", textDecoration: "none", fontSize: "0.875rem", fontWeight: 600 }}
          >
            + OT urgente
          </Link>
        </div>
      </div>

      {error && (
        <div style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#dc2626", padding: "0.75rem", borderRadius: "0.5rem", marginBottom: "1rem", fontSize: "0.875rem" }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: "2rem", color: "#6b7280" }}>Cargando...</div>
      ) : wos.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: "#6b7280" }}>No tenés OT asignadas.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {wos.map((wo) => (
            <Link
              key={wo.id}
              href={`/tecnico/ot/${wo.id}`}
              style={{ display: "block", background: "white", border: "1px solid #e5e7eb", borderRadius: "0.75rem", padding: "1rem", textDecoration: "none", color: "inherit" }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: 600 }}>OT #{wo.number}</span>
                {wo.priority_code === "URGENT" && (
                  <span style={{ background: "#fef2f2", color: "#dc2626", padding: "0.125rem 0.5rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: 700 }}>
                    Urgente
                  </span>
                )}
              </div>
              <div style={{ fontSize: "0.875rem", color: "#6b7280", marginTop: "0.25rem" }}>{wo.requested_description}</div>
              <div style={{ fontSize: "0.75rem", color: "#9ca3af", marginTop: "0.375rem" }}>{wo.status_label || wo.status_code}</div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
