"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { AssetCreate, Location, AssetType } from "@/lib/types";

export default function NewAssetPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([]);

  const [form, setForm] = useState<AssetCreate>({ location_id: "", name: "", description: "", brand: "", model: "", serial_number: "", internal_code: "", qr_code: "", notes: "", asset_type_id: undefined });

  async function loadRefs() {
    try {
      const [locs, types] = await Promise.all([api.get<Location[]>("/locations"), api.get<AssetType[]>("/asset-types")]);
      setLocations(locs); setAssetTypes(types);
    } catch (e) { console.error(e); }
  }

  useEffect(() => { loadRefs(); }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(null); setLoading(true);
    try { const res = await api.post<{ id: string }>("/assets", form); router.push(`/dashboard/assets/${res.id}`); router.refresh(); }
    catch (e) { setError(e instanceof Error ? e.message : "Error al crear activo"); }
    finally { setLoading(false); }
  }

  return (
    <div style={{ padding: "1rem", maxWidth: "700px", margin: "0 auto" }}>
      <h1>Nuevo Activo</h1>
      {error && <div style={{ background: theme.dangerBg, color: theme.danger, padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="asset-location" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Ubicación *</label>
          <select id="asset-location" value={form.location_id} onChange={e=>setForm({...form, location_id: e.target.value})} required style={{ width: "100%", padding: "0.75rem" }}>
            <option value="">Seleccionar ubicación</option>
            {locations.map(l=>(<option key={l.id} value={l.id}>{l.name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="asset-name" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Nombre *</label>
          <input id="asset-name" value={form.name} onChange={e=>setForm({...form, name: e.target.value})} required style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="asset-type" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Tipo de activo</label>
          <select id="asset-type" value={form.asset_type_id || ""} onChange={e=>setForm({...form, asset_type_id: e.target.value || undefined})} style={{ width: "100%", padding: "0.75rem" }}>
            <option value="">Seleccionar tipo</option>
            {assetTypes.map(t=>(<option key={t.id} value={t.id}>{t.label}</option>))}
          </select>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
          <div><label htmlFor="asset-brand" style={{ display: "block", marginBottom: "0.25rem" }}>Marca</label><input id="asset-brand" value={form.brand} onChange={e=>setForm({...form, brand: e.target.value})} style={{ width: "100%", padding: "0.75rem" }} /></div>
          <div><label htmlFor="asset-model" style={{ display: "block", marginBottom: "0.25rem" }}>Modelo</label><input id="asset-model" value={form.model} onChange={e=>setForm({...form, model: e.target.value})} style={{ width: "100%", padding: "0.75rem" }} /></div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
          <div><label htmlFor="asset-serial" style={{ display: "block", marginBottom: "0.25rem" }}>Número de serie</label><input id="asset-serial" value={form.serial_number} onChange={e=>setForm({...form, serial_number: e.target.value})} style={{ width: "100%", padding: "0.75rem" }} /></div>
          <div><label htmlFor="asset-internal-code" style={{ display: "block", marginBottom: "0.25rem" }}>Código interno</label><input id="asset-internal-code" value={form.internal_code} onChange={e=>setForm({...form, internal_code: e.target.value})} style={{ width: "100%", padding: "0.75rem" }} /></div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
          <div><label htmlFor="asset-qr" style={{ display: "block", marginBottom: "0.25rem" }}>QR Code</label><input id="asset-qr" value={form.qr_code} onChange={e=>setForm({...form, qr_code: e.target.value})} style={{ width: "100%", padding: "0.75rem" }} /></div>
          <div><label htmlFor="asset-status" style={{ display: "block", marginBottom: "0.25rem" }}>Estado</label>
            <select id="asset-status" value={form.status || "ACTIVE"} onChange={e=>setForm({...form, status: e.target.value as "ACTIVE"|"INACTIVE"|"RETIRED"})} style={{ width: "100%", padding: "0.75rem" }}>
              <option value="ACTIVE">Activo</option><option value="INACTIVE">Inactivo</option><option value="RETIRED">Retirado</option>
            </select>
          </div>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="asset-description" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Descripción</label>
          <textarea id="asset-description" value={form.description} onChange={e=>setForm({...form, description: e.target.value})} rows={3} style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        <div style={{ marginBottom: "1.5rem" }}>
          <label htmlFor="asset-notes" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Observaciones</label>
          <textarea id="asset-notes" value={form.notes} onChange={e=>setForm({...form, notes: e.target.value})} rows={3} style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <button type="submit" disabled={loading} style={{ flex: 1, padding: "1rem", background: theme.primary, opacity: loading ? 0.6 : 1, color: theme.primaryText, border: "none", borderRadius: "0.5rem" }}>{loading?"Guardando...":"Crear Activo"}</button>
          <Link href="/dashboard/assets" style={{ flex: 1, padding: "1rem", background: theme.bg, textAlign: "center", textDecoration: "none", borderRadius: "0.5rem" }}>Cancelar</Link>
        </div>
      </form>
    </div>
  );
}