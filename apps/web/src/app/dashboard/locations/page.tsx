"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Location, Customer } from "@/lib/types";

export default function LocationsPage() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterCustomer, setFilterCustomer] = useState<string>("");

  useEffect(() => { loadCustomers(); loadLocations(); }, [filterCustomer]);

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

  return (
    <div style={{ padding: "1rem", maxWidth: "900px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
        <h1>Ubicaciones</h1>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <select value={filterCustomer} onChange={e=>setFilterCustomer(e.target.value)} style={{ padding: "0.5rem", minWidth: "250px" }}>
            <option value="">Todas los clientes</option>
            {customers.map(c=>(<option key={c.person_id} value={c.person_id}>{c.display_name}</option>))}
          </select>
          <Link href="/dashboard/locations/new">
            <button style={{ background: "#2563eb", color: "white", border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem" }}>+ Nueva Ubicación</button>
          </Link>
        </div>
      </div>

      {error && <div style={{ background: "#fef2f2", color: "#dc2626", padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}

      {loading ? <div style={{ textAlign: "center", padding: "2rem" }}>Cargando...</div> : locations.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: "#6b7280" }}>No hay ubicaciones. <Link href="/dashboard/locations/new">Crear primera</Link></div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {locations.map(l=>(<li key={l.id} style={{ border: "1px solid #e5e7eb", borderRadius: "0.5rem", padding: "1rem", marginBottom: "0.75rem", background: "white" }}>
            <Link href={`/dashboard/locations/${l.id}`} style={{ textDecoration: "none", color: "inherit" }}>
              <div style={{ fontWeight: 600, fontSize: "1.1rem" }}>{l.name}</div>
              <div style={{ color: "#6b7280", fontSize: "0.875rem", marginTop: "0.25rem" }}>
                {l.address && `${l.address}`}
                {l.city && `, ${l.city}`}
                {l.province && `, ${l.province}`}
              </div>
              <div style={{ marginTop: "0.5rem", fontSize: "0.875rem", color: "#6b7280" }}>
                Cliente: {customers.find(c=>c.person_id===l.customer_id)?.display_name || l.customer_id}
              </div>
            </Link>
          </li>))}
        </ul>
      )}
    </div>
  );
}