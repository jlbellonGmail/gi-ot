"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { Customer, Location, Asset, WorkOrderType, Priority, WorkOrderCreate } from "@/lib/types";

// El técnico no elige tipo de trabajo ni prioridad: el backend fuerza
// prioridad URGENT y autoasignación (POST /work-orders con rol
// TENANT_TECHNICIAN — ROADMAP §06). Se envía un tipo/prioridad por
// defecto solo para satisfacer el esquema; el backend los ignora.
export default function NuevaOTUrgentePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const prefillAssetId = searchParams.get("asset_id");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [customers, setCustomers] = useState<Customer[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [defaultTypeId, setDefaultTypeId] = useState<string>("");
  const [defaultPriorityId, setDefaultPriorityId] = useState<string>("");

  const [customerId, setCustomerId] = useState("");
  const [locationId, setLocationId] = useState("");
  const [assetId, setAssetId] = useState("");
  const [description, setDescription] = useState("");

  async function loadRefs() {
    try {
      const [custs, locs, asts, types, pris] = await Promise.all([
        api.get<Customer[]>("/customers"),
        api.get<Location[]>("/locations"),
        api.get<Asset[]>("/assets"),
        api.get<WorkOrderType[]>("/work-order-types"),
        api.get<Priority[]>("/priorities"),
      ]);
      setCustomers(custs);
      setLocations(locs);
      setAssets(asts);
      setDefaultTypeId(types[0]?.id || "");
      setDefaultPriorityId(pris[0]?.id || "");

      if (prefillAssetId) {
        const asset = asts.find((a) => a.id === prefillAssetId);
        const location = asset ? locs.find((l) => l.id === asset.location_id) : undefined;
        if (asset && location) {
          setCustomerId(location.customer_id);
          setLocationId(location.id);
          setAssetId(asset.id);
        }
      }
    } catch (e) { console.error(e); }
  }

  useEffect(() => { loadRefs(); }, []);

  const locationsForCustomer = locations.filter((l) => l.customer_id === customerId);
  const assetsForLocation = assets.filter((a) => a.location_id === locationId);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(null); setLoading(true);
    try {
      const payload: WorkOrderCreate = {
        customer_id: customerId,
        location_id: locationId,
        asset_id: assetId,
        work_order_type_id: defaultTypeId,
        priority_id: defaultPriorityId,
        requested_description: description,
      };
      const res = await api.post<{ id: string }>("/work-orders", payload);
      router.push(`/tecnico/ot/${res.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al crear la OT urgente");
    } finally { setLoading(false); }
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.25rem", marginBottom: "0.25rem" }}>OT urgente</h1>
      <p style={{ fontSize: "0.875rem", color: theme.textSecondary, marginBottom: "1rem" }}>
        Se crea con prioridad Urgente y asignada a vos.
      </p>

      {error && (
        <div style={{ background: theme.dangerBg, border: `1px solid ${theme.danger}`, color: theme.danger, padding: "0.75rem", borderRadius: "0.5rem", marginBottom: "1rem", fontSize: "0.875rem" }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="urgente-customer" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Cliente *</label>
          <select
            id="urgente-customer"
            value={customerId}
            onChange={(e) => { setCustomerId(e.target.value); setLocationId(""); setAssetId(""); }}
            required
            style={{ padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", width: "100%", fontSize: "1rem" }}
          >
            <option value="">Seleccionar cliente</option>
            {customers.map((c) => (<option key={c.person_id} value={c.person_id}>{c.display_name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="urgente-location" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Ubicación *</label>
          <select
            id="urgente-location"
            value={locationId}
            onChange={(e) => { setLocationId(e.target.value); setAssetId(""); }}
            required
            disabled={!customerId}
            style={{ padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", width: "100%", fontSize: "1rem" }}
          >
            <option value="">Seleccionar ubicación</option>
            {locationsForCustomer.map((l) => (<option key={l.id} value={l.id}>{l.name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="urgente-asset" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Activo *</label>
          <select
            id="urgente-asset"
            value={assetId}
            onChange={(e) => setAssetId(e.target.value)}
            required
            disabled={!locationId}
            style={{ padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", width: "100%", fontSize: "1rem" }}
          >
            <option value="">Seleccionar activo</option>
            {assetsForLocation.map((a) => (<option key={a.id} value={a.id}>{a.name}</option>))}
          </select>
        </div>
        <div style={{ marginBottom: "1.5rem" }}>
          <label htmlFor="urgente-description" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Descripción *</label>
          <textarea
            id="urgente-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            required
            placeholder="¿Qué está pasando?"
            style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.5rem", fontSize: "1rem" }}
          />
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            type="submit"
            disabled={loading || !defaultTypeId || !defaultPriorityId}
            style={{ flex: 1, padding: "1rem", background: theme.danger, opacity: loading ? 0.6 : 1, color: theme.primaryText, border: "none", borderRadius: "0.5rem", fontSize: "1rem", fontWeight: 600, cursor: loading ? "not-allowed" : "pointer" }}
          >
            {loading ? "Creando..." : "Crear OT urgente"}
          </button>
          <a
            href="/tecnico"
            style={{ flex: 1, padding: "1rem", background: theme.bg, color: theme.text, border: "none", borderRadius: "0.5rem", fontSize: "1rem", textAlign: "center", textDecoration: "none" }}
          >
            Cancelar
          </a>
        </div>
      </form>
    </div>
  );
}
