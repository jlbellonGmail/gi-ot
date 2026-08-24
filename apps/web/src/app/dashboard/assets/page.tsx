"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { FilterButton, FilterPanel, FilterChips } from "@/components/FilterPanel";
import { Asset, AssetType, Location } from "@/lib/types";

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterLoc, setFilterLoc] = useState<string>("");
  const [filterType, setFilterType] = useState<string>("");
  const [draftFilterLoc, setDraftFilterLoc] = useState<string>("");
  const [draftFilterType, setDraftFilterType] = useState<string>("");
  const [filtersOpen, setFiltersOpen] = useState(false);

  async function loadRefs() {
    try {
      const [locs, types] = await Promise.all([
        api.get<Location[]>("/locations"),
        api.get<AssetType[]>("/asset-types"),
      ]);
      setLocations(locs);
      setAssetTypes(types);
    } catch (e) { console.error(e); }
  }

  async function loadAssets() {
    try {
      setLoading(true);
      let url = "/assets";
      const params = [];
      if (filterLoc) params.push(`location_id=${filterLoc}`);
      if (filterType) params.push(`asset_type_id=${filterType}`);
      if (params.length) url += "?" + params.join("&");
      const data = await api.get<Asset[]>(url);
      setAssets(data);
    } catch (e) { setError(e instanceof Error ? e.message : "Error al cargar activos"); }
    finally { setLoading(false); }
  }

  useEffect(() => { loadRefs(); loadAssets(); }, [filterLoc, filterType]);

  function openFilters() { setDraftFilterLoc(filterLoc); setDraftFilterType(filterType); setFiltersOpen(true); }
  function applyFilters() { setFilterLoc(draftFilterLoc); setFilterType(draftFilterType); setFiltersOpen(false); }
  function clearFilters() { setFilterLoc(""); setFilterType(""); setDraftFilterLoc(""); setDraftFilterType(""); setFiltersOpen(false); }
  const activeFilterCount = (filterLoc ? 1 : 0) + (filterType ? 1 : 0);

  return (
    <div style={{ padding: "1rem", maxWidth: "1000px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
        <h1>Activos</h1>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <FilterButton activeCount={activeFilterCount} onClick={openFilters} />
          <Link href="/dashboard/assets/new">
            <button style={{ background: theme.primary, color: theme.primaryText, border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem" }}>+ Nuevo Activo</button>
          </Link>
        </div>
      </div>

      {activeFilterCount > 0 && (
        <FilterChips
          chips={[
            ...(filterLoc ? [{ key: "loc", label: `Ubicación: ${locations.find((l) => l.id === filterLoc)?.name || "—"}` }] : []),
            ...(filterType ? [{ key: "type", label: `Tipo: ${assetTypes.find((t) => t.id === filterType)?.label || "—"}` }] : []),
          ]}
          onRemove={(key) => { if (key === "loc") setFilterLoc(""); if (key === "type") setFilterType(""); }}
          onClearAll={clearFilters}
        />
      )}

      <FilterPanel open={filtersOpen} onClose={() => setFiltersOpen(false)} onApply={applyFilters} onClear={clearFilters}>
        <div>
          <label htmlFor="asset-filter-loc" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Ubicación</label>
          <select id="asset-filter-loc" value={draftFilterLoc} onChange={(e) => setDraftFilterLoc(e.target.value)} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }}>
            <option value="">Todas las ubicaciones</option>
            {locations.map((l) => (<option key={l.id} value={l.id}>{l.name}</option>))}
          </select>
        </div>
        <div>
          <label htmlFor="asset-filter-type" style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.875rem", color: theme.textSecondary }}>Tipo</label>
          <select id="asset-filter-type" value={draftFilterType} onChange={(e) => setDraftFilterType(e.target.value)} style={{ width: "100%", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", background: theme.surface, color: theme.text }}>
            <option value="">Todos los tipos</option>
            {assetTypes.map((t) => (<option key={t.id} value={t.id}>{t.label}</option>))}
          </select>
        </div>
      </FilterPanel>

      {error && <ErrorBanner message={error} onRetry={loadAssets} />}

      {loading ? <div style={{ textAlign: "center", padding: "2rem" }}>Cargando...</div> : assets.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>No hay activos. <Link href="/dashboard/assets/new">Crear primero</Link></div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {assets.map(a=>(<li key={a.id} style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem", marginBottom: "0.75rem", background: theme.surface }}>
            <Link href={`/dashboard/assets/${a.id}`} style={{ textDecoration: "none", color: "inherit" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: "1.1rem" }}>{a.name}</div>
                  <div style={{ color: theme.textSecondary, fontSize: "0.875rem", marginTop: "0.25rem" }}>
                    {a.asset_type && `Tipo: ${a.asset_type.label}`}
                    {a.brand && ` • Marca: ${a.brand}`}
                    {a.model && ` • Modelo: ${a.model}`}
                  </div>
                </div>
                <span style={{
                  background: a.status==="ACTIVE"?theme.successBg:a.status==="INACTIVE"?theme.dangerBg:theme.bg,
                  color: a.status==="ACTIVE"?theme.success:a.status==="INACTIVE"?theme.danger:theme.textSecondary,
                  padding: "0.25rem 0.75rem", borderRadius: "9999px", fontSize: "0.75rem"
                }}>{a.status}</span>
              </div>
              <div style={{ marginTop: "0.5rem", fontSize: "0.875rem", color: theme.textSecondary }}>
                Ubicación: {locations.find(l=>l.id===a.location_id)?.name || a.location_id}
                {a.serial_number && ` • Serie: ${a.serial_number}`}
                {a.qr_code && ` • QR: ${a.qr_code}`}
              </div>
            </Link>
          </li>))}
        </ul>
      )}
    </div>
  );
}