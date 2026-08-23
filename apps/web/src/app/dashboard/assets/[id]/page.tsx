"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Asset, Location, AssetType } from "@/lib/types";

export default function AssetDetailPage() {
  const params = useParams(); const router = useRouter(); const id = params.id as string;
  const [asset, setAsset] = useState<Asset | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);

  const [form, setForm] = useState({ name: "", description: "", brand: "", model: "", serial_number: "", internal_code: "", qr_code: "", notes: "", asset_type_id: "", status: "ACTIVE" });

  useEffect(() => { load(); }, [id]);

  async function load() {
    try {
      setLoading(true);
      const [assetData, locs, types] = await Promise.all([
        api.get<Asset>(`/assets/${id}`),
        api.get<Location[]>("/locations"),
        api.get<AssetType[]>("/asset-types"),
      ]);
      setAsset(assetData);
      setLocations(locs);
      setAssetTypes(types);
      setForm({
        name: assetData.name, description: assetData.description || "", brand: assetData.brand || "",
        model: assetData.model || "", serial_number: assetData.serial_number || "",
        internal_code: assetData.internal_code || "", qr_code: assetData.qr_code || "",
        notes: assetData.notes || "", asset_type_id: assetData.asset_type_id || "",
        status: assetData.status,
      });
    } catch (e) { setError(e instanceof Error ? e.message : "Error al cargar"); }
    finally { setLoading(false); }
  }

  async function save() {
    try { setSaving(true); setError(null); await api.patch(`/assets/${id}`, form); await load(); setEditMode(false); }
    catch (e) { setError(e instanceof Error ? e.message : "Error al guardar"); }
    finally { setSaving(false); }
  }

  if (loading) return <div style={{ padding: "1rem", textAlign: "center" }}>Cargando...</div>;
  if (!asset) return <div style={{ padding: "1rem" }}>No encontrado</div>;

  const loc = locations.find(l => l.id === asset.location_id);
  const at = assetTypes.find(t => t.id === asset.asset_type_id);

  return (
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1>{asset.name}</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={()=>setEditMode(!editMode)} style={{ padding: "0.5rem 1rem" }}>{editMode?"Cancelar":"Editar"}</button>
          <button onClick={()=>router.back()} style={{ padding: "0.5rem 1rem", background: "#f3f4f6" }}>Volver</button>
        </div>
      </div>
      {error && <div style={{ background: "#fef2f2", color: "#dc2626", padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}
      <div style={{ border: "1px solid #e5e7eb", borderRadius: "0.5rem", padding: "1rem" }}>
        <dl style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: "0.5rem 1rem" }}>
          <dt>Ubicación</dt><dd>{loc?.name || asset.location_id}</dd>
          <dt>Tipo</dt><dd>{at?.label || asset.asset_type_id || "—"}</dd>
          <dt>Marca</dt><dd>{asset.brand || "—"}</dd>
          <dt>Modelo</dt><dd>{asset.model || "—"}</dd>
          <dt>N° Serie</dt><dd>{asset.serial_number || "—"}</dd>
          <dt>Código int.</dt><dd>{asset.internal_code || "—"}</dd>
          <dt>QR</dt><dd>{asset.qr_code || "—"}</dd>
          <dt>Estado</dt><dd><span style={{ background: asset.status==="ACTIVE"?"#dcfce7":asset.status==="INACTIVE"?"#fef2f2":"#f3f4f6", color: asset.status==="ACTIVE"?"#166534":asset.status==="INACTIVE"?"#dc2626":"#6b7280", padding: "0.125rem 0.5rem", borderRadius: "9999px", fontSize: "0.875rem" }}>{asset.status}</span></dd>
          <dt>Descripción</dt><dd>{asset.description || "—"}</dd>
          <dt>Observaciones</dt><dd>{asset.notes || "—"}</dd>
        </dl>
        {editMode && (
          <div style={{ marginTop: "1rem", display: "grid", gap: "0.75rem" }}>
            <input value={form.name} onChange={e=>setForm({...form, name: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} />
            <select value={form.asset_type_id} onChange={e=>setForm({...form, asset_type_id: e.target.value})} style={{ width: "100%", padding: "0.5rem" }}>
              <option value="">Sin tipo</option>
              {assetTypes.map(t=>(<option key={t.id} value={t.id}>{t.label}</option>))}
            </select>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <input value={form.brand} onChange={e=>setForm({...form, brand: e.target.value})} placeholder="Marca" style={{ padding: "0.5rem" }} />
              <input value={form.model} onChange={e=>setForm({...form, model: e.target.value})} placeholder="Modelo" style={{ padding: "0.5rem" }} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <input value={form.serial_number} onChange={e=>setForm({...form, serial_number: e.target.value})} placeholder="Serie" style={{ padding: "0.5rem" }} />
              <input value={form.internal_code} onChange={e=>setForm({...form, internal_code: e.target.value})} placeholder="Código int." style={{ padding: "0.5rem" }} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <input value={form.qr_code} onChange={e=>setForm({...form, qr_code: e.target.value})} placeholder="QR" style={{ padding: "0.5rem" }} />
              <select value={form.status} onChange={e=>setForm({...form, status: e.target.value as "ACTIVE"|"INACTIVE"|"RETIRED"})} style={{ padding: "0.5rem" }}>
                <option value="ACTIVE">Activo</option><option value="INACTIVE">Inactivo</option><option value="RETIRED">Retirado</option>
              </select>
            </div>
            <textarea value={form.description} onChange={e=>setForm({...form, description: e.target.value})} rows={2} placeholder="Descripción" style={{ width: "100%", padding: "0.5rem" }} />
            <textarea value={form.notes} onChange={e=>setForm({...form, notes: e.target.value})} rows={2} placeholder="Observaciones" style={{ width: "100%", padding: "0.5rem" }} />
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button onClick={save} disabled={saving} style={{ padding: "0.5rem 1.5rem", background: "#7c3aed", color: "white", border: "none", borderRadius: "0.375rem" }}>{saving?"Guardando...":"Guardar"}</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}