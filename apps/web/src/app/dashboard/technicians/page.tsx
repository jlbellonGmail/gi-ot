"use client";

import { theme } from "@/lib/theme";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { FilterButton, FilterPanel, FilterChips } from "@/components/FilterPanel";
import { SortButton } from "@/components/SortButton";
import { Technician } from "@/lib/types";

type SortValue = "name_asc" | "name_desc" | "recent";
const SORT_OPTIONS: { value: SortValue; label: string }[] = [
  { value: "name_asc", label: "Nombre A-Z" },
  { value: "name_desc", label: "Nombre Z-A" },
  { value: "recent", label: "Más recientes" },
];

export default function TechniciansPage() {
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeOnly, setActiveOnly] = useState(true);
  const [draftActiveOnly, setDraftActiveOnly] = useState(true);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<SortValue>("name_asc");

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

  function openFilters() { setDraftActiveOnly(activeOnly); setFiltersOpen(true); }
  function applyFilters() { setActiveOnly(draftActiveOnly); setFiltersOpen(false); }
  function clearFilters() { setActiveOnly(false); setDraftActiveOnly(false); setFiltersOpen(false); }

  const visibleTechnicians = useMemo(() => {
    let list = technicians;
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter((t) =>
        t.display_name.toLowerCase().includes(q) ||
        (t.email || "").toLowerCase().includes(q) ||
        (t.phone || "").toLowerCase().includes(q) ||
        (t.license_number || "").toLowerCase().includes(q) ||
        (t.profession || "").toLowerCase().includes(q)
      );
    }
    const sorted = [...list];
    if (sort === "name_asc") sorted.sort((a, b) => a.display_name.localeCompare(b.display_name));
    else if (sort === "name_desc") sorted.sort((a, b) => b.display_name.localeCompare(a.display_name));
    else if (sort === "recent") sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    return sorted;
  }, [technicians, search, sort]);

  return (
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.75rem" }}>
        <h1>Técnicos</h1>
        <Link href="/dashboard/technicians/new" style={{ textDecoration: "none" }}>
          <button style={{ background: theme.successSolid, color: theme.primaryText, border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem", fontSize: "1rem", cursor: "pointer" }}>
            + Nuevo Técnico
          </button>
        </Link>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem", flexWrap: "wrap" }}>
        <input
          type="search"
          placeholder="Buscar por nombre, email, teléfono, matrícula o profesión..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: "1 1 260px", padding: "0.625rem 0.875rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", fontSize: "0.9375rem", background: theme.surface, color: theme.text }}
        />
        <FilterButton activeCount={activeOnly ? 1 : 0} onClick={openFilters} />
        <SortButton value={sort} options={SORT_OPTIONS} onChange={setSort} />
      </div>

      {activeOnly && (
        <FilterChips
          chips={[{ key: "activeOnly", label: "Solo activos" }]}
          onRemove={() => setActiveOnly(false)}
          onClearAll={clearFilters}
        />
      )}

      <FilterPanel open={filtersOpen} onClose={() => setFiltersOpen(false)} onApply={applyFilters} onClear={clearFilters}>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.9375rem" }}>
          <input type="checkbox" checked={draftActiveOnly} onChange={(e) => setDraftActiveOnly(e.target.checked)} />
          Mostrar solo técnicos activos
        </label>
      </FilterPanel>

      {error && <ErrorBanner message={error} onRetry={loadTechnicians} />}

      {loading ? (
        <div style={{ textAlign: "center", padding: "2rem" }}>Cargando...</div>
      ) : technicians.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>
          No hay técnicos registrados.
          <br />
          <Link href="/dashboard/technicians/new">Crear el primero</Link>
        </div>
      ) : visibleTechnicians.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>
          No hay técnicos que coincidan con la búsqueda o los filtros.
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {visibleTechnicians.map((t) => (
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