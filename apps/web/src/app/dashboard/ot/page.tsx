"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Customer, Location, Asset, WorkOrderStatus, WorkOrder } from "@/lib/types";

export default function OTListPage() {
  const [wos, setWOs] = useState<WorkOrder[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [statuses, setStatuses] = useState<WorkOrderStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState("");
  const [filterCustomer, setFilterCustomer] = useState("");
  const [filterLocation, setFilterLocation] = useState("");
  const [filterAsset, setFilterAsset] = useState("");

  useEffect(() => { loadRefs(); }, []);
  useEffect(() => { loadWOs(); }, [filterStatus, filterCustomer, filterLocation, filterAsset]);

  async function loadRefs() {
    try {
      const [custs, locs, asts, status] = await Promise.all([
        api.get<Customer[]>("/customers"),
        api.get<Location[]>("/locations"),
        api.get<Asset[]>("/assets"),
        api.get<WorkOrderStatus[]>("/work-order-statuses"),
      ]);
      setCustomers(custs); setLocations(locs); setAssets(asts); setStatuses(status);
    } catch (e) { console.error(e); }
  }

  async function loadWOs() {
    try {
      setLoading(true);
      let url = "/work-orders";
      const params = [];
      if (filterStatus) params.push(`status_code=${filterStatus}`);
      if (filterCustomer) params.push(`customer_id=${filterCustomer}`);
      if (filterLocation) params.push(`location_id=${filterLocation}`);
      if (filterAsset) params.push(`asset_id=${filterAsset}`);
      if (params.length) url += "?" + params.join("&");
      const data = await api.get<WorkOrder[]>(url);
      setWOs(data);
    } catch (e) { setError(e instanceof Error ? e.message : "Error al cargar OT"); }
    finally { setLoading(false); }
  }

  return (
    <div style={{ padding: "1rem", maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "1rem" }}>
        <h1>Órdenes de Trabajo</h1>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
          <select value={filterStatus} onChange={e=>setFilterStatus(e.target.value)} style={{ padding: "0.5rem", minWidth: "150px" }}>
            <option value="">Todos los estados</option>
            {statuses.map(s=>(<option key={s.code} value={s.code}>{s.label}</option>))}
          </select>
          <select value={filterCustomer} onChange={e=>setFilterCustomer(e.target.value)} style={{ padding: "0.5rem", minWidth: "200px" }}>
            <option value="">Todos los clientes</option>
            {customers.map(c=>(<option key={c.person_id} value={c.person_id}>{c.display_name}</option>))}
          </select>
          <select value={filterLocation} onChange={e=>setFilterLocation(e.target.value)} style={{ padding: "0.5rem", minWidth: "200px" }}>
            <option value="">Todas ubicaciones</option>
            {locations.map(l=>(<option key={l.id} value={l.id}>{l.name}</option>))}
          </select>
          <select value={filterAsset} onChange={e=>setFilterAsset(e.target.value)} style={{ padding: "0.5rem", minWidth: "200px" }}>
            <option value="">Todos los activos</option>
            {assets.map(a=>(<option key={a.id} value={a.id}>{a.name}</option>))}
          </select>
          <Link href="/dashboard/ot/new" style={{ textDecoration: "none" }}>
            <button style={{ background: "#16a34a", color: "white", border: "none", padding: "0.75rem 1.5rem", borderRadius: "0.5rem", fontSize: "1rem", cursor: "pointer" }}>
              + Nueva OT
            </button>
          </Link>
        </div>
      </div>

      {error && <div style={{ background: "#fef2f2", color: "#dc2626", padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}

      {loading ? <div style={{ textAlign: "center", padding: "2rem" }}>Cargando...</div> : wos.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: "#6b7280" }}>No hay OT. <Link href="/dashboard/ot/new">Crear primera</Link></div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {wos.map(w=>(
            <li key={w.id} style={{ border: "1px solid #e5e7eb", borderRadius: "0.5rem", marginBottom: "0.75rem", background: "white" }}>
              <Link href={`/dashboard/ot/${w.id}`} style={{ textDecoration: "none", color: "inherit", display: "flex", justifyContent: "space-between", alignItems: "flex-start", padding: "1rem" }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: "1.1rem" }}>OT #{w.number}</div>
                  <div style={{ color: "#6b7280", fontSize: "0.875rem", marginTop: "0.25rem" }}>
                    {w.requested_description}
                    {w.performed_description && ` • ${w.performed_description.substring(0,30)}...`}
                  </div>
                  <div style={{ marginTop: "0.5rem", fontSize: "0.875rem", color: "#6b7280" }}>
                    Cli: {w.customer_id.substring(0,8)}... {w.location_id && `Loc:${w.location_id.substring(0,8)}`} {w.asset_id && `Act:${w.asset_id.substring(0,8)}`}
                    {w.technician_id && ` • Tec:${w.technician_id.substring(0,4)}...`}
                    {w.scheduled_at && ` • Prog:${w.scheduled_at}`}
                    {w.started_at && ` • Inicio:${w.started_at}`}
                    {w.finished_at && ` • Fin:${w.finished_at}`}
                  </div>
                </div>
                <span style={{
                  background: w.status_code==="PENDING"?"#dcfce7":w.status_code==="IN_PROGRESS"?"#fef3cf":w.status_code==="COMPLETED"?"#dcfce7":w.status_code==="UNRESOLVED"?"#fef2f2":"#f3f4f6",
                  color: w.status_code==="PENDING"?"#166534":w.status_code==="IN_PROGRESS"?"#92400e":w.status_code==="COMPLETED"?"#166534":w.status_code==="UNRESOLVED"?"#dc2626":"#6b7280",
                  padding: "0.25rem 0.75rem", borderRadius: "9999px", fontSize: "0.75rem"
                }}>{w.status_code}</span>
              </Link>
            </li>))}
        </ul>
      )}
    </div>
  );
}
