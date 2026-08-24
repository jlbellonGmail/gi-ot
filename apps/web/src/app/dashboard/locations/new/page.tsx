"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { LocationCreate, Customer } from "@/lib/types";

export default function NewLocationPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);

  const [form, setForm] = useState<LocationCreate>({ customer_id: "", name: "", address: "", city: "", province: "", notes: "" });

  async function loadCustomers() {
    try { const data = await api.get<Customer[]>("/customers"); setCustomers(data); }
    catch (e) { console.error(e); }
  }

  useEffect(() => { loadCustomers(); }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(null); setLoading(true);
    try { const res = await api.post<{ id: string }>("/locations", form); router.push(`/dashboard/locations/${res.id}`); router.refresh(); }
    catch (e) { setError(e instanceof Error ? e.message : "Error al crear ubicación"); }
    finally { setLoading(false); }
  }

  return (
    <div style={{ padding: "1rem", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Nueva Ubicación</h1>
      {error && <div style={{ background: theme.dangerBg, color: theme.danger, padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="location-customer" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Cliente *</label>
          <select id="location-customer" value={form.customer_id} onChange={e=>setForm({...form, customer_id: e.target.value})} required style={{ width: "100%", padding: "0.75rem" }}>
            <option value="">Seleccionar cliente</option>
            {customers.map(c=>(<option key={c.person_id} value={c.person_id}>{c.display_name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="location-name" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Nombre *</label>
          <input id="location-name" value={form.name} onChange={e=>setForm({...form, name: e.target.value})} required style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="location-address" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Dirección</label>
          <input id="location-address" value={form.address} onChange={e=>setForm({...form, address: e.target.value})} style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
          <div><label htmlFor="location-city" style={{ display: "block", marginBottom: "0.25rem" }}>Ciudad</label><input id="location-city" value={form.city} onChange={e=>setForm({...form, city: e.target.value})} style={{ width: "100%", padding: "0.75rem" }} /></div>
          <div><label htmlFor="location-province" style={{ display: "block", marginBottom: "0.25rem" }}>Provincia</label><input id="location-province" value={form.province} onChange={e=>setForm({...form, province: e.target.value})} style={{ width: "100%", padding: "0.75rem" }} /></div>
        </div>
        <div style={{ marginBottom: "1.5rem" }}>
          <label htmlFor="location-notes" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Observaciones</label>
          <textarea id="location-notes" value={form.notes} onChange={e=>setForm({...form, notes: e.target.value})} rows={3} style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <button type="submit" disabled={loading} style={{ flex: 1, padding: "1rem", background: theme.primary, opacity: loading ? 0.6 : 1, color: theme.primaryText, border: "none", borderRadius: "0.5rem" }}>{loading?"Guardando...":"Crear Ubicación"}</button>
          <Link href="/dashboard/locations" style={{ flex: 1, padding: "1rem", background: theme.bg, textAlign: "center", textDecoration: "none", borderRadius: "0.5rem" }}>Cancelar</Link>
        </div>
      </form>
    </div>
  );
}