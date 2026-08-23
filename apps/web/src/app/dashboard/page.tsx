"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { theme } from "@/lib/theme";
import { WorkOrder } from "@/lib/types";

interface Indicator {
  key: string;
  label: string;
  count: number;
  href: string;
  fg: string;
  bg: string;
}

// Panel principal de Oficina/Admin (ROADMAP §07): orientado a situación
// operativa, no a navegación — cada indicador lleva al subconjunto de OT
// correspondiente en el listado (UI-UX-STANDARDS §33: reconocer → decidir → actuar).
export default function DashboardPanelPage() {
  const [wos, setWos] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true); setError(null);
        const data = await api.get<WorkOrder[]>("/work-orders");
        setWos(data);
      } catch (e) { setError(e instanceof Error ? e.message : "Error al cargar el panel"); }
      finally { setLoading(false); }
    })();
  }, []);

  const indicators: Indicator[] = useMemo(() => {
    const pending = wos.filter((w) => w.status_code === "PENDING").length;
    const inProgress = wos.filter((w) => w.status_code === "IN_PROGRESS").length;
    const urgent = wos.filter((w) => w.priority_code === "URGENT" && !w.is_terminal).length;
    const unresolved = wos.filter((w) => w.status_code === "UNRESOLVED").length;
    return [
      { key: "pending", label: "Pendientes", count: pending, href: "/dashboard/ot?status=PENDING", fg: theme.success, bg: theme.successBg },
      { key: "in_progress", label: "En curso", count: inProgress, href: "/dashboard/ot?status=IN_PROGRESS", fg: theme.warning, bg: theme.warningBg },
      { key: "urgent", label: "Urgentes", count: urgent, href: "/dashboard/ot?priority_code=URGENT", fg: theme.danger, bg: theme.dangerBg },
      { key: "unresolved", label: "Requieren atención", count: unresolved, href: "/dashboard/ot?status=UNRESOLVED", fg: theme.danger, bg: theme.dangerBg },
    ];
  }, [wos]);

  const openCount = wos.filter((w) => !w.is_terminal).length;

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "0.75rem" }}>
        <div>
          <h1 style={{ color: theme.text }}>Panel</h1>
          <p style={{ color: theme.textSecondary, fontSize: "0.9375rem", marginTop: "0.125rem" }}>
            {loading ? "Cargando situación operativa..." : `${openCount} OT abiertas en total`}
          </p>
        </div>
        <Link href="/dashboard/ot/new" style={{ textDecoration: "none" }}>
          <button style={{ background: theme.success, color: theme.primaryText, border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem", fontSize: "1rem", cursor: "pointer", fontWeight: 600 }}>
            + Nueva OT
          </button>
        </Link>
      </div>

      {error && <div style={{ background: theme.dangerBg, color: theme.danger, padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}

      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem", color: theme.textSecondary }}>Cargando...</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.875rem", marginBottom: "1.5rem" }}>
          {indicators.map((ind) => (
            <Link key={ind.key} href={ind.href} style={{ textDecoration: "none" }}>
              <div style={{ background: theme.surface, border: `1px solid ${theme.border}`, borderRadius: "0.75rem", padding: "1.25rem" }}>
                <div style={{ fontSize: "2rem", fontWeight: 700, color: ind.fg }}>{ind.count}</div>
                <div style={{ marginTop: "0.25rem", fontSize: "0.9375rem", color: theme.text }}>{ind.label}</div>
              </div>
            </Link>
          ))}
        </div>
      )}

      <Link href="/dashboard/ot" style={{ color: theme.primary, fontSize: "0.9375rem", textDecoration: "underline" }}>
        Ver todas las Órdenes de Trabajo →
      </Link>
    </div>
  );
}
