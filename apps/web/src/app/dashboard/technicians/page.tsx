"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Technician } from "@/lib/types";

export default function TechniciansPage() {
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeOnly, setActiveOnly] = useState(true);

  async function loadTechnicians() {
    try {
      setLoading(true);
      const data = await api.get<Technician[]>(`/technicians?active_only=${activeOnly}`);
      setTechnicians(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar técnicos");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTechnicians();
  }, [activeOnly]);

  return (
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1>Técnicos</h1>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "0.25rem", fontSize: "0.875rem" }}>
            <input type="checkbox" checked={activeOnly} onChange={(e) => setActiveOnly(e.target.checked)} />
            Solo activos
          </label>
          <Link href="/dashboard/technicians/new" style={{ textDecoration: "none" }}>
            <button style={{ background: theme.success, color: theme.primaryText, border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem", fontSize: "1rem", cursor: "pointer" }}>
              + Nuevo Técnico
            </button>
          </Link>
        </div>
      </div>

      {error && <div style={{ background: theme.dangerBg, border: `1px solid ${theme.danger}`, color: theme.danger, padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}

      {loading ? (
        <div style={{ textAlign: "center", padding: "2rem" }}>Cargando...</div>
      ) : technicians.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>
          No hay técnicos registrados.
          <br />
          <Link href="/dashboard/technicians/new">Crear el primero</Link>
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {technicians.map((t) => (
            <li key={t.person_id} style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem", marginBottom: "0.75rem", background: theme.surface }}>
              <Link href={`/dashboard/technicians/${t.person_id}`} style={{ textDecoration: "none", color: "inherit" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: "1.1rem" }}>{t.display_name}</div>
                    <div style={{ color: theme.textSecondary, fontSize: "0.875rem", marginTop: "0.25rem" }}>
                      {t.profession && `${t.profession} • `}
                      {t.email && `${t.email} • `}
                      {t.phone && t.phone}
                    </div>
                  </div>
                  <span style={{
                    background: t.technician_status === "ACTIVE" ? theme.successBg : theme.dangerBg,
                    color: t.technician_status === "ACTIVE" ? theme.success : theme.danger,
                    padding: "0.25rem 0.75rem",
                    borderRadius: "9999px",
                    fontSize: "0.75rem",
                  }}>
                    {t.technician_status}
                  </span>
                </div>
                {t.license_number && <div style={{ marginTop: "0.5rem", fontSize: "0.875rem", color: theme.textSecondary }}>Matrícula: {t.license_number}</div>}
                <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  {t.identifications.map((ident) => (
                    <span key={ident.id} style={{ background: theme.successBg, color: theme.success, padding: "0.25rem 0.5rem", borderRadius: "0.25rem", fontSize: "0.75rem" }}>
                      {ident.identification_type}: {ident.identification_value}
                    </span>
                  ))}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}