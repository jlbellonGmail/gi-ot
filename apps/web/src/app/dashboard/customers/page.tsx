"use client";

import { theme } from "@/lib/theme";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Customer } from "@/lib/types";
import { ErrorBanner } from "@/components/ErrorBanner";
import { FilterButton, FilterPanel, FilterChips } from "@/components/FilterPanel";
import { SortButton } from "@/components/SortButton";

type SortValue = "name_asc" | "name_desc" | "recent";
const SORT_OPTIONS: { value: SortValue; label: string }[] = [
  { value: "name_asc", label: "Nombre A-Z" },
  { value: "name_desc", label: "Nombre Z-A" },
  { value: "recent", label: "Más recientes" },
];

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<string>("");
  const [draftStatus, setDraftStatus] = useState<string>("");
  const [sort, setSort] = useState<SortValue>("name_asc");
  const [filtersOpen, setFiltersOpen] = useState(false);

  async function loadCustomers() {
    try {
      setLoading(true);
      const data = await api.get<Customer[]>("/customers");
      setCustomers(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar clientes");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCustomers();
  }, []);

  function openFilters() { setDraftStatus(status); setFiltersOpen(true); }
  function applyFilters() { setStatus(draftStatus); setFiltersOpen(false); }
  function clearFilters() { setStatus(""); setDraftStatus(""); setFiltersOpen(false); }

  const visibleCustomers = useMemo(() => {
    let list = customers;
    if (status) list = list.filter((c) => c.status === status);
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter((c) =>
        c.display_name.toLowerCase().includes(q) ||
        (c.email || "").toLowerCase().includes(q) ||
        (c.phone || "").toLowerCase().includes(q) ||
        c.identifications.some((i) => i.identification_value.toLowerCase().includes(q))
      );
    }
    const sorted = [...list];
    if (sort === "name_asc") sorted.sort((a, b) => a.display_name.localeCompare(b.display_name));
    else if (sort === "name_desc") sorted.sort((a, b) => b.display_name.localeCompare(a.display_name));
    else if (sort === "recent") sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    return sorted;
  }, [customers, search, status, sort]);

  return (
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.75rem" }}>
        <h1>Clientes</h1>
        <Link href="/dashboard/customers/new" style={{ textDecoration: "none" }}>
          <button style={{ background: theme.primary, color: theme.primaryText, border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem", fontSize: "1rem", cursor: "pointer" }}>
            + Nuevo Cliente
          </button>
        </Link>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem", flexWrap: "wrap" }}>
        <input
          type="search"
          placeholder="Buscar por nombre, email, teléfono o identificación..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: "1 1 260px", padding: "0.625rem 0.875rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", fontSize: "0.9375rem", background: theme.surface, color: theme.text }}
        />
        <FilterButton activeCount={status ? 1 : 0} onClick={openFilters} />
        <SortButton value={sort} options={SORT_OPTIONS} onChange={setSort} />
      </div>

      {status && (
        <FilterChips
          chips={[{ key: "status", label: `Estado: ${status === "ACTIVE" ? "Activo" : "Inactivo"}` }]}
          onRemove={() => setStatus("")}
          onClearAll={clearFilters}
        />
      )}

      <FilterPanel open={filtersOpen} onClose={() => setFiltersOpen(false)} onApply={applyFilters} onClear={clearFilters}>
        <div>
          <label htmlFor="customer-filter-status" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Estado</label>
          <select id="customer-filter-status" value={draftStatus} onChange={(e) => setDraftStatus(e.target.value)} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }}>
            <option value="">Todos</option>
            <option value="ACTIVE">Activo</option>
            <option value="INACTIVE">Inactivo</option>
          </select>
        </div>
      </FilterPanel>

      {error && <ErrorBanner message={error} onRetry={loadCustomers} />}

      {loading ? (
        <div style={{ textAlign: "center", padding: "2rem" }}>Cargando...</div>
      ) : customers.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>
          No hay clientes registrados.
          <br />
          <Link href="/dashboard/customers/new">Crear el primero</Link>
        </div>
      ) : visibleCustomers.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>
          No hay clientes que coincidan con la búsqueda o los filtros.
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {visibleCustomers.map((c) => (
            <li key={c.person_id} style={{
              border: `1px solid ${theme.border}`,
              borderRadius: "0.5rem",
              padding: "1rem",
              marginBottom: "0.75rem",
              background: theme.surface,
            }}>
              <Link href={`/dashboard/customers/${c.person_id}`} style={{ textDecoration: "none", color: "inherit" }}>
                <div style={{ fontWeight: 600, fontSize: "1.1rem" }}>{c.display_name}</div>
                <div style={{ color: theme.textSecondary, fontSize: "0.875rem", marginTop: "0.25rem" }}>
                  {c.person_type === "LEGAL" ? "Persona Jurídica" : "Persona Física"}
                  {c.email && ` • ${c.email}`}
                  {c.phone && ` • ${c.phone}`}
                </div>
                <div style={{ marginTop: "0.5rem", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                  {c.identifications.map((ident) => (
                    <span key={ident.id} style={{
                      background: theme.infoBg,
                      color: theme.text,
                      padding: "0.25rem 0.5rem",
                      borderRadius: "0.25rem",
                      fontSize: "0.75rem",
                    }}>
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
