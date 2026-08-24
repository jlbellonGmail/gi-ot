"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Location, Customer } from "@/lib/types";

export default function LocationDetailPage() {
  const params = useParams(); const router = useRouter(); const id = params.id as string;
  const [loc, setLoc] = useState<Location | null>(null);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);

  const [form, setForm] = useState({ name: "", address: "", city: "", province: "", notes: "" });

  useEffect(() => { load(); }, [id]);

  async function load() {
    try {
      setLoading(true);
      const [locData, custData] = await Promise.all([
        api.get<Location>(`/locations/${id}`),
        api.get<Customer[]>("/customers"),
      ]);
      setLoc(locData);
      setForm({ name: locData.name, address: locData.address || "", city: locData.city || "", province: locData.province || "", notes: locData.notes || "" });
      setCustomer(custData.find(c => c.person_id === locData.customer_id) || null);
    } catch (e) { setError(e instanceof Error ? e.message : "Error al cargar"); }
    finally { setLoading(false); }
  }

  async function save() {
    try { setSaving(true); setError(null); await api.patch(`/locations/${id}`, form); await load(); setEditMode(false); }
    catch (e) { setError(e instanceof Error ? e.message : "Error al guardar"); }
    finally { setSaving(false); }
  }

  if (loading) return <div style={{ padding: "1rem", textAlign: "center" }}>Cargando...</div>;
  if (!loc) return <div style={{ padding: "1rem" }}>No encontrado</div>;

  return (
    <div style={{ padding: "1rem", maxWidth: "700px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1>{loc.name}</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={()=>setEditMode(!editMode)} style={{ padding: "0.5rem 1rem" }}>{editMode?"Cancelar":"Editar"}</button>
          <button onClick={()=>router.back()} style={{ padding: "0.5rem 1rem", background: theme.bg }}>Volver</button>
        </div>
      </div>
      {error && <ErrorBanner message={error} onRetry={load} />}
      <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem" }}>
        <dl style={{ display: "grid", gridTemplateColumns: "120px 1fr", gap: "0.5rem 1rem" }}>
          <dt>Dirección</dt><dd>{loc.address || "—"}</dd>
          <dt>Ciudad</dt><dd>{loc.city || "—"}</dd>
          <dt>Provincia</dt><dd>{loc.province || "—"}</dd>
          <dt>Cliente</dt><dd>{customer?.display_name || loc.customer_id}</dd>
          <dt>Observaciones</dt><dd>{loc.notes || "—"}</dd>
        </dl>
        {editMode && (
          <div style={{ marginTop: "1rem", display: "grid", gap: "0.75rem" }}>
            <input value={form.name} onChange={e=>setForm({...form, name: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} />
            <input value={form.address} onChange={e=>setForm({...form, address: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <input value={form.city} onChange={e=>setForm({...form, city: e.target.value})} placeholder="Ciudad" style={{ width: "100%", padding: "0.5rem" }} />
              <input value={form.province} onChange={e=>setForm({...form, province: e.target.value})} placeholder="Provincia" style={{ width: "100%", padding: "0.5rem" }} />
            </div>
            <textarea value={form.notes} onChange={e=>setForm({...form, notes: e.target.value})} rows={3} style={{ width: "100%", padding: "0.5rem" }} placeholder="Observaciones" />
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button onClick={save} disabled={saving} style={{ padding: "0.5rem 1.5rem", background: theme.primary, color: theme.primaryText, border: "none", borderRadius: "0.375rem" }}>{saving?"Guardando...":"Guardar"}</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}