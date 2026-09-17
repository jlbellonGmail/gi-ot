"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Customer, Location, Asset, Technician, WorkOrderType, Priority, WorkOrderCreate } from "@/lib/types";

export default function NewOTPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [customers, setCustomers] = useState<Customer[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [types, setTypes] = useState<WorkOrderType[]>([]);
  const [priorities, setPriorities] = useState<Priority[]>([]);

  const [form, setForm] = useState<WorkOrderCreate>({
    customer_id: "",
    location_id: "",
    asset_id: "",
    work_order_type_id: "",
    priority_id: "",
    requested_description: "",
    scheduled_at: undefined,
    technician_id: undefined,
  });

  async function loadRefs() {
    try {
      const [custs, locs, asts, techs, woTypes, pris] = await Promise.all([
        api.get<Customer[]>("/customers"),
        api.get<Location[]>("/locations"),
        api.get<Asset[]>("/assets"),
        api.get<Technician[]>("/technicians?active_only=true"),
        api.get<WorkOrderType[]>("/work-order-types"),
        api.get<Priority[]>("/priorities"),
      ]);
      setCustomers(custs);
      setLocations(locs);
      setAssets(asts);
      setTechnicians(techs);
      setTypes(woTypes);
      setPriorities(pris);
    } catch (e) { console.error(e); }
  }

  useEffect(() => { loadRefs(); }, []);

  const locationsForCustomer = locations.filter((l) => l.customer_id === form.customer_id);
  const assetsForLocation = assets.filter((a) => a.location_id === form.location_id);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(null); setLoading(true);
    try {
      const res = await api.post<{ id: string }>("/work-orders", {
        ...form,
        scheduled_at: form.scheduled_at || undefined,
        technician_id: form.technician_id || undefined,
      });
      router.push(`/dashboard/ot/${res.id}`);
      router.refresh();
    } catch (e) { setError(e instanceof Error ? e.message : "Error al crear OT"); }
    finally { setLoading(false); }
  }

  return (
    <div style={{ padding: "1rem", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Nueva Orden de Trabajo</h1>
      {error && <ErrorBanner message={error} />}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="wo-customer" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Cliente *</label>
          <select
            id="wo-customer"
            value={form.customer_id}
            onChange={(e) => setForm({ ...form, customer_id: e.target.value, location_id: "", asset_id: "" })}
            required
            style={{ padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", width: "100%" }}
          >
            <option value="">Seleccionar cliente</option>
            {customers.map((c) => (<option key={c.person_id} value={c.person_id}>{c.display_name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="wo-location" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Ubicación *</label>
          <select
            id="wo-location"
            value={form.location_id}
            onChange={(e) => setForm({ ...form, location_id: e.target.value, asset_id: "" })}
            required
            disabled={!form.customer_id}
            style={{ padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", width: "100%" }}
          >
            <option value="">Seleccionar ubicación</option>
            {locationsForCustomer.map((l) => (<option key={l.id} value={l.id}>{l.name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="wo-asset" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Activo *</label>
          <select
            id="wo-asset"
            value={form.asset_id}
            onChange={(e) => setForm({ ...form, asset_id: e.target.value })}
            required
            disabled={!form.location_id}
            style={{ padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", width: "100%" }}
          >
            <option value="">Seleccionar activo</option>
            {assetsForLocation.map((a) => (<option key={a.id} value={a.id}>{a.name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="wo-type" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Tipo OT *</label>
          <select
            id="wo-type"
            value={form.work_order_type_id}
            onChange={(e) => setForm({ ...form, work_order_type_id: e.target.value })}
            required
            style={{ padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", width: "100%" }}
          >
            <option value="">Seleccionar tipo</option>
            {types.map((t) => (<option key={t.id} value={t.id}>{t.label}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="wo-priority" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Prioridad *</label>
          <select
            id="wo-priority"
            value={form.priority_id}
            onChange={(e) => setForm({ ...form, priority_id: e.target.value })}
            required
            style={{ padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", width: "100%" }}
          >
            <option value="">Seleccionar prioridad</option>
            {priorities.map((p) => (<option key={p.id} value={p.id}>{p.label}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="wo-technician" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Técnico asignado</label>
          <select
            id="wo-technician"
            value={form.technician_id || ""}
            onChange={(e) => setForm({ ...form, technician_id: e.target.value || undefined })}
            style={{ padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", width: "100%" }}
          >
            <option value="">Sin asignar (asignar luego)</option>
            {technicians.map((t) => (<option key={t.person_id} value={t.person_id}>{t.display_name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="wo-description" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Descripción solicitada *</label>
          <textarea
            id="wo-description"
            value={form.requested_description}
            onChange={(e) => setForm({ ...form, requested_description: e.target.value })}
            rows={3}
            required
            style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", fontSize: "1rem" }}
          />
        </div>
        <div style={{ marginBottom: "1.5rem" }}>
          <label htmlFor="wo-scheduled" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Programado para</label>
          <input
            id="wo-scheduled"
            type="datetime-local"
            value={form.scheduled_at || ""}
            onChange={(e) => setForm({ ...form, scheduled_at: e.target.value || undefined })}
            style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", fontSize: "1rem" }}
          />
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              flex: 1,
              padding: "1rem",
              background: theme.primary, opacity: loading ? 0.6 : 1,
              color: theme.primaryText,
              border: "none",
              borderRadius: "0.5rem",
              fontSize: "1rem",
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Guardando..." : "Crear OT"}
          </button>
          <Link
            href="/dashboard/ot"
            style={{
              flex: 1,
              padding: "1rem",
              background: theme.bg,
              color: theme.text,
              border: "none",
              borderRadius: "0.5rem",
              fontSize: "1rem",
              textAlign: "center",
              textDecoration: "none",
            }}
          >
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}
