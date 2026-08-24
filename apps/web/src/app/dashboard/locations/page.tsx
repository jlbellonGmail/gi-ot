"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { FilterButton, FilterPanel, FilterChips } from "@/components/FilterPanel";
import { Location, Customer } from "@/lib/types";

export default function LocationsPage() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterCustomer, setFilterCustomer] = useState<string>("");
  const [draftFilterCustomer, setDraftFilterCustomer] = useState<string>("");
  const [filtersOpen, setFiltersOpen] = useState(false);

  async function loadCustomers() {
    try { const data = await api.get<Customer[]>("/customers"); setCustomers(data); }
    catch (e) { console.error(e); }
  }

  async function loadLocations() {
    try {
      setLoading(true);
      const url = filterCustomer ? `/locations?customer_id=${filterCustomer}` : "/locations";
      const data = await api.get<Location[]>(url);
      setLocations(data);
    } catch (e) { setError(e instanceof Error ? e.message : "Error al cargar ubicaciones"); }
    finally { setLoading(false); }
  }

  useEffect(() => { loadCustomers(); loadLocations(); }, [filterCustomer]);

  function openFilters() { setDraftFilterCustomer(filterCustomer); setFiltersOpen(true); }
  function applyFilters() { setFilterCustomer(draftFilterCustomer); setFiltersOpen(false); }
  function clearFilters() { setFilterCustomer(""); setDraftFilterCustomer(""); setFiltersOpen(false); }

  return (
    <div style={{ padding: "1rem", maxWidth: "900px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
        <h1>Ubicaciones</h1>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <FilterButton activeCount={filterCustomer ? 1 : 0} onClick={openFilters} />
          <Link href="/dashboard/locations/new">
            <button style={{ background: theme.primary, color: theme.primaryText, border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem" }}>+ Nueva Ubicación</button>
          </Link>
        </div>
      </div>

      {filterCustomer && (
        <FilterChips
          chips={[{ key: "customer", label: `Cliente: ${customers.find((c) => c.person_id === filterCustomer)?.display_name || "—"}` }]}
          onRemove={() => setFilterCustomer("")}
          onClearAll={clearFilters}
        />
      )}

      <FilterPanel open={filtersOpen} onClose={() => setFiltersOpen(false)} onApply={applyFilters} onClear={clearFilters}>
        <div>
          <label htmlFor="loc-filter-customer" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Cliente</label>
          <select id="loc-filter-customer" value={draftFilterCustomer} onChange={(e) => setDraftFilterCustomer(e.target.value)} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }}>
            <option value="">Todos los clientes</option>
            {customers.map((c) => (<option key={c.person_id} value={c.person_id}>{c.display_name}</option>))}
          </select>
        </div>
      </FilterPanel>

      {error && <ErrorBanner message={error} onRetry={loadLocations} />}

      {loading ? <div style={{ textAlign: "center", padding: "2rem" }}>Cargando...</div> : locations.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>No hay ubicaciones. <Link href="/dashboard/locations/new">Crear primera</Link></div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {locations.map(l=>(<li key={l.id} style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem", marginBottom: "0.75rem", background: theme.surface }}>
            <Link href={`/dashboard/locations/${l.id}`} style={{ textDecoration: "none", color: "inherit" }}>
              <div style={{ fontWeight: 600, fontSize: "1.1rem" }}>{l.name}</div>
              <div style={{ color: theme.textSecondary, fontSize: "0.875rem", marginTop: "0.25rem" }}>
                {l.address && `${l.address}`}
                {l.city && `, ${l.city}`}
                {l.province && `, ${l.province}`}
              </div>
              <div style={{ marginTop: "0.5rem", fontSize: "0.875rem", color: theme.textSecondary }}>
                Cliente: {customers.find(c=>c.person_id===l.customer_id)?.display_name || l.customer_id}
              </div>
            </Link>
          </li>))}
        </ul>
      )}
    </div>
  );
}