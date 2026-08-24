"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { theme } from "@/lib/theme";
import { Customer, Location, Asset, Technician, Priority, WorkOrderStatus, WorkOrder } from "@/lib/types";
import { StatusBadge, PriorityBadge } from "@/components/StatusPriorityBadge";

const SORT_OPTIONS: { value: string; label: string }[] = [
  { value: "", label: "Más recientes" },
  { value: "date_asc", label: "Más antiguas" },
  { value: "priority", label: "Prioridad" },
  { value: "updated", label: "Actualización reciente" },
  { value: "status", label: "Estado" },
];

interface Filters {
  status: string;
  priority: string;
  technician: string;
  customer: string;
  dateFrom: string;
  dateTo: string;
}

const EMPTY_FILTERS: Filters = { status: "", priority: "", technician: "", customer: "", dateFrom: "", dateTo: "" };

export default function OTListPage() {
  const [wos, setWos] = useState<WorkOrder[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [statuses, setStatuses] = useState<WorkOrderStatus[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [draftFilters, setDraftFilters] = useState<Filters>(EMPTY_FILTERS);
  const [sort, setSort] = useState("");
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [sortOpen, setSortOpen] = useState(false);

  const searchDebounce = useRef<ReturnType<typeof setTimeout> | null>(null);
  const searchParams = useSearchParams();

  async function loadRefs() {
    try {
      const [custs, locs, asts, techs, pris, sts] = await Promise.all([
        api.get<Customer[]>("/customers"),
        api.get<Location[]>("/locations"),
        api.get<Asset[]>("/assets"),
        api.get<Technician[]>("/technicians?active_only=true"),
        api.get<Priority[]>("/priorities"),
        api.get<WorkOrderStatus[]>("/work-order-statuses"),
      ]);
      setCustomers(custs); setLocations(locs); setAssets(asts);
      setTechnicians(techs); setPriorities(pris); setStatuses(sts);

      // Deep-link desde el Panel principal (?status=CODE, ?priority_code=CODE):
      // se aplica una sola vez, al resolver los catálogos necesarios.
      const statusParam = searchParams.get("status");
      const priorityCodeParam = searchParams.get("priority_code");
      if (statusParam || priorityCodeParam) {
        setFilters((f) => ({
          ...f,
          status: statusParam || f.status,
          priority: priorityCodeParam ? pris.find((p) => p.code === priorityCodeParam)?.id || f.priority : f.priority,
        }));
      }
    } catch (e) { console.error(e); }
  }

  const loadWos = useCallback(async () => {
    try {
      setLoading(true); setError(null);
      const params = new URLSearchParams();
      if (search) params.set("q", search);
      if (filters.status) params.set("status_code", filters.status);
      if (filters.priority) params.set("priority_id", filters.priority);
      if (filters.technician) params.set("technician_id", filters.technician);
      if (filters.customer) params.set("customer_id", filters.customer);
      if (filters.dateFrom) params.set("date_from", filters.dateFrom);
      if (filters.dateTo) params.set("date_to", filters.dateTo);
      if (sort) params.set("sort", sort);
      const qs = params.toString();
      const data = await api.get<WorkOrder[]>(`/work-orders${qs ? `?${qs}` : ""}`);
      setWos(data);
    } catch (e) { setError(e instanceof Error ? e.message : "Error al cargar OT"); }
    finally { setLoading(false); }
  }, [search, filters, sort]);

  useEffect(() => { loadRefs(); }, []);
  useEffect(() => { loadWos(); }, [loadWos]);

  function onSearchChange(value: string) {
    setSearchInput(value);
    if (searchDebounce.current) clearTimeout(searchDebounce.current);
    searchDebounce.current = setTimeout(() => setSearch(value), 350);
  }

  function openFilters() { setDraftFilters(filters); setFiltersOpen(true); }
  function applyFilters() { setFilters(draftFilters); setFiltersOpen(false); }
  function clearAllFilters() { setFilters(EMPTY_FILTERS); setDraftFilters(EMPTY_FILTERS); setFiltersOpen(false); }
  function removeFilter(key: keyof Filters) { setFilters((f) => ({ ...f, [key]: "" })); }

  const activeFilterCount = useMemo(
    () => Object.values(filters).filter((v) => v !== "").length,
    [filters]
  );

  const activeFilterChips = useMemo(() => {
    const chips: { key: keyof Filters; label: string }[] = [];
    if (filters.status) {
      const s = statuses.find((x) => x.code === filters.status);
      chips.push({ key: "status", label: `Estado: ${s?.label || filters.status}` });
    }
    if (filters.priority) {
      const p = priorities.find((x) => x.id === filters.priority);
      chips.push({ key: "priority", label: `Prioridad: ${p?.label || "—"}` });
    }
    if (filters.technician) {
      const t = technicians.find((x) => x.person_id === filters.technician);
      chips.push({ key: "technician", label: `Técnico: ${t?.display_name || "—"}` });
    }
    if (filters.customer) {
      const c = customers.find((x) => x.person_id === filters.customer);
      chips.push({ key: "customer", label: `Cliente: ${c?.display_name || "—"}` });
    }
    if (filters.dateFrom) chips.push({ key: "dateFrom", label: `Desde: ${filters.dateFrom}` });
    if (filters.dateTo) chips.push({ key: "dateTo", label: `Hasta: ${filters.dateTo}` });
    return chips;
  }, [filters, statuses, priorities, technicians, customers]);

  function customerName(id: string) { return customers.find((c) => c.person_id === id)?.display_name || "—"; }
  function locationName(id: string) { return locations.find((l) => l.id === id)?.name || "—"; }
  function assetName(id: string) { return assets.find((a) => a.id === id)?.name || "—"; }
  function technicianName(id: string | null) { return id ? technicians.find((t) => t.person_id === id)?.display_name || "—" : "Sin asignar"; }

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.75rem" }}>
        <h1 style={{ color: theme.text }}>Órdenes de Trabajo</h1>
        <Link href="/dashboard/ot/new" style={{ textDecoration: "none" }}>
          <button style={{ background: theme.success, color: theme.primaryText, border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem", fontSize: "1rem", cursor: "pointer", fontWeight: 600 }}>
            + Nueva OT
          </button>
        </Link>
      </div>

      {/* Búsqueda + control compacto de filtros/orden — UI-UX-STANDARDS §9-15 */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem", flexWrap: "wrap" }}>
        <input
          type="search"
          placeholder="Buscar por número, cliente, ubicación o activo..."
          value={searchInput}
          onChange={(e) => onSearchChange(e.target.value)}
          style={{ flex: "1 1 260px", padding: "0.625rem 0.875rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", fontSize: "0.9375rem", background: theme.surface, color: theme.text }}
        />
        <div style={{ position: "relative" }}>
          <button
            onClick={openFilters}
            style={{ padding: "0.625rem 1rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", background: activeFilterCount ? theme.primary : theme.surface, color: activeFilterCount ? theme.primaryText : theme.text, cursor: "pointer", fontSize: "0.9375rem", fontWeight: 500 }}
          >
            Filtros{activeFilterCount ? ` ${activeFilterCount}` : ""}
          </button>
        </div>
        <div style={{ position: "relative" }}>
          <button
            onClick={() => setSortOpen((v) => !v)}
            style={{ padding: "0.625rem 1rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", background: theme.surface, color: theme.text, cursor: "pointer", fontSize: "0.9375rem", fontWeight: 500 }}
          >
            Ordenar: {SORT_OPTIONS.find((o) => o.value === sort)?.label}
          </button>
          {sortOpen && (
            <>
              <div onClick={() => setSortOpen(false)} style={{ position: "fixed", inset: 0, zIndex: 20 }} />
              <div style={{ position: "absolute", right: 0, top: "calc(100% + 0.25rem)", background: theme.surface, border: `1px solid ${theme.border}`, borderRadius: "0.5rem", boxShadow: "0 4px 16px rgba(0,0,0,0.15)", zIndex: 21, minWidth: "200px", overflow: "hidden" }}>
                {SORT_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => { setSort(opt.value); setSortOpen(false); }}
                    style={{ display: "block", width: "100%", textAlign: "left", padding: "0.625rem 0.875rem", background: opt.value === sort ? theme.bg : "transparent", border: "none", color: theme.text, cursor: "pointer", fontSize: "0.875rem" }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Chips de filtros activos — UI-UX-STANDARDS §13 */}
      {activeFilterChips.length > 0 && (
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          {activeFilterChips.map((chip) => (
            <span key={chip.key} style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", background: theme.bg, border: `1px solid ${theme.border}`, borderRadius: "9999px", padding: "0.25rem 0.5rem 0.25rem 0.75rem", fontSize: "0.8125rem", color: theme.text }}>
              {chip.label}
              <button onClick={() => removeFilter(chip.key)} aria-label={`Quitar filtro ${chip.label}`} style={{ background: "transparent", border: "none", cursor: "pointer", color: theme.textSecondary, fontSize: "0.9375rem", lineHeight: 1, padding: "0.125rem" }}>×</button>
            </span>
          ))}
          <button onClick={clearAllFilters} style={{ background: "transparent", border: "none", color: theme.primary, cursor: "pointer", fontSize: "0.8125rem", textDecoration: "underline" }}>
            Limpiar todos
          </button>
        </div>
      )}

      {/* Panel de filtros — bottom sheet en mobile, popover anclado en desktop (UI-UX-STANDARDS §14) */}
      {filtersOpen && (
        <>
          <div onClick={() => setFiltersOpen(false)} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)", zIndex: 30 }} />
          <div style={{
            position: "fixed", zIndex: 31, background: theme.surface, color: theme.text,
            left: "50%", transform: "translateX(-50%)",
            bottom: 0, top: "auto", width: "100%", maxWidth: "420px",
            borderRadius: "1rem 1rem 0 0", padding: "1.25rem", maxHeight: "80vh", overflowY: "auto",
            boxShadow: "0 -4px 24px rgba(0,0,0,0.2)",
          }}>
            <h3 style={{ marginBottom: "1rem" }}>Filtros</h3>
            <div style={{ display: "grid", gap: "0.875rem" }}>
              <div>
                <label htmlFor="filter-status" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Estado</label>
                <select id="filter-status" value={draftFilters.status} onChange={(e) => setDraftFilters((f) => ({ ...f, status: e.target.value }))} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }}>
                  <option value="">Todos</option>
                  {statuses.map((s) => (<option key={s.code} value={s.code}>{s.label}</option>))}
                </select>
              </div>
              <div>
                <label htmlFor="filter-priority" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Prioridad</label>
                <select id="filter-priority" value={draftFilters.priority} onChange={(e) => setDraftFilters((f) => ({ ...f, priority: e.target.value }))} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }}>
                  <option value="">Todas</option>
                  {priorities.map((p) => (<option key={p.id} value={p.id}>{p.label}</option>))}
                </select>
              </div>
              <div>
                <label htmlFor="filter-technician" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Técnico</label>
                <select id="filter-technician" value={draftFilters.technician} onChange={(e) => setDraftFilters((f) => ({ ...f, technician: e.target.value }))} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }}>
                  <option value="">Todos</option>
                  {technicians.map((t) => (<option key={t.person_id} value={t.person_id}>{t.display_name}</option>))}
                </select>
              </div>
              <div>
                <label htmlFor="filter-customer" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Cliente</label>
                <select id="filter-customer" value={draftFilters.customer} onChange={(e) => setDraftFilters((f) => ({ ...f, customer: e.target.value }))} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }}>
                  <option value="">Todos</option>
                  {customers.map((c) => (<option key={c.person_id} value={c.person_id}>{c.display_name}</option>))}
                </select>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
                <div>
                  <label htmlFor="filter-date-from" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Desde</label>
                  <input id="filter-date-from" type="date" value={draftFilters.dateFrom} onChange={(e) => setDraftFilters((f) => ({ ...f, dateFrom: e.target.value }))} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }} />
                </div>
                <div>
                  <label htmlFor="filter-date-to" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Hasta</label>
                  <input id="filter-date-to" type="date" value={draftFilters.dateTo} onChange={(e) => setDraftFilters((f) => ({ ...f, dateTo: e.target.value }))} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }} />
                </div>
              </div>
            </div>
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "1.25rem" }}>
              <button onClick={applyFilters} style={{ flex: 1, padding: "0.75rem", background: theme.primary, color: theme.primaryText, border: "none", borderRadius: "0.5rem", fontWeight: 600, cursor: "pointer" }}>
                Aplicar
              </button>
              <button onClick={clearAllFilters} style={{ padding: "0.75rem 1rem", background: "transparent", border: `1px solid ${theme.border}`, color: theme.text, borderRadius: "0.5rem", cursor: "pointer" }}>
                Limpiar
              </button>
            </div>
          </div>
        </>
      )}

      {error && <div style={{ background: theme.dangerBg, color: theme.danger, padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}

      {loading ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>Cargando...</div>
      ) : wos.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>
          {search || activeFilterCount ? "No hay OT que coincidan con la búsqueda o los filtros." : (
            <>No hay OT todavía. <Link href="/dashboard/ot/new" style={{ color: theme.primary }}>Crear la primera</Link></>
          )}
        </div>
      ) : (
        <div style={{ display: "grid", gap: "0.75rem" }}>
          {wos.map((w) => {
            return (
              <Link key={w.id} href={`/dashboard/ot/${w.id}`} style={{ textDecoration: "none", color: "inherit" }}>
                <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.75rem", background: theme.surface, padding: "1rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.75rem", flexWrap: "wrap" }}>
                    <div style={{ fontWeight: 600, fontSize: "1.0625rem", color: theme.text }}>OT #{w.number}</div>
                    <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap" }}>
                      <PriorityBadge code={w.priority_code} label={w.priority_label} />
                      <StatusBadge code={w.status_code} label={w.status_label} />
                    </div>
                  </div>
                  <div style={{ marginTop: "0.5rem", fontSize: "0.9375rem", color: theme.text }}>{customerName(w.customer_id)}</div>
                  <div style={{ marginTop: "0.125rem", fontSize: "0.8125rem", color: theme.textSecondary }}>
                    {locationName(w.location_id)} • {assetName(w.asset_id)}
                  </div>
                  <div style={{ marginTop: "0.375rem", fontSize: "0.8125rem", color: theme.textSecondary, display: "flex", flexWrap: "wrap", gap: "0.25rem 0.75rem" }}>
                    <span>Técnico: {technicianName(w.technician_id)}</span>
                    <span>{new Date(w.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
