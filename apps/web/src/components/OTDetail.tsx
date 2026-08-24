"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import {
  Customer,
  Location,
  Asset,
  WorkOrderType,
  Priority,
  Technician,
  WorkOrder,
  WorkOrderHistoryEntry,
  WorkOrderPhoto,
  CurrentUser,
} from "@/lib/types";
import { StatusBadge, PriorityBadge } from "@/components/StatusPriorityBadge";
import { ErrorBanner } from "@/components/ErrorBanner";

// Detalle de OT compartido entre /dashboard/ot/[id] (Oficina/Admin) y
// /tecnico/ot/[id] (Técnico) — cada ruta lo envuelve en su propio shell
// (desktop vs mobile-first, ROADMAP §06). Las acciones de oficina
// (asignar técnico, reabrir) ya están gateadas por rol, así que el
// componente es seguro para ambos contextos sin lógica adicional.
export default function OTDetail() {
  const params = useParams();
  const id = params.id as string;

  const [wo, setWo] = useState<WorkOrder | null>(null);
  const [history, setHistory] = useState<WorkOrderHistoryEntry[]>([]);
  const [photos, setPhotos] = useState<WorkOrderPhoto[]>([]);
  const [photoUrls, setPhotoUrls] = useState<Record<string, string>>({});
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [types, setTypes] = useState<WorkOrderType[]>([]);
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [me, setMe] = useState<CurrentUser | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const [assignTechId, setAssignTechId] = useState("");
  const [performedDescription, setPerformedDescription] = useState("");
  const [reopenNotes, setReopenNotes] = useState("");

  useEffect(() => { load(); }, [id]);

  useEffect(() => {
    let cancelled = false;
    const urls: Record<string, string> = {};
    (async () => {
      for (const p of photos) {
        try {
          const blob = await api.getBlob(`/work-orders/${id}/photos/${p.id}/file`);
          if (cancelled) return;
          urls[p.id] = URL.createObjectURL(blob);
        } catch (e) { console.error(e); }
      }
      if (!cancelled) setPhotoUrls(urls);
    })();
    return () => {
      cancelled = true;
      Object.values(urls).forEach((u) => URL.revokeObjectURL(u));
    };
  }, [photos, id]);

  async function load() {
    try {
      setLoading(true);
      setError(null);
      const [custs, locs, asts, techs, typ, pri, meResp] = await Promise.all([
        api.get<Customer[]>("/customers"),
        api.get<Location[]>("/locations"),
        api.get<Asset[]>("/assets"),
        api.get<Technician[]>("/technicians?active_only=true"),
        api.get<WorkOrderType[]>("/work-order-types"),
        api.get<Priority[]>("/priorities"),
        api.get<CurrentUser>("/auth/me"),
      ]);
      setCustomers(custs);
      setLocations(locs);
      setAssets(asts);
      setTechnicians(techs);
      setTypes(typ);
      setPriorities(pri);
      setMe(meResp);

      const w = await api.get<WorkOrder>(`/work-orders/${id}`);
      setWo(w);
      setPerformedDescription(w.performed_description || "");

      const h = await api.get<WorkOrderHistoryEntry[]>(`/work-orders/${id}/history`);
      setHistory(h);

      const ph = await api.get<WorkOrderPhoto[]>(`/work-orders/${id}/photos`);
      setPhotos(ph);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar OT");
    } finally { setLoading(false); }
  }

  async function runAction(fn: () => Promise<unknown>) {
    try {
      setActionLoading(true);
      setError(null);
      await fn();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al ejecutar la acción");
    } finally { setActionLoading(false); }
  }

  async function handlePhotoSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      setUploadingPhoto(true);
      setError(null);
      const formData = new FormData();
      formData.append("file", file);
      await api.upload(`/work-orders/${id}/photos`, formData);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al subir la foto");
    } finally { setUploadingPhoto(false); }
  }

  async function handleDeletePhoto(photoId: string) {
    try {
      setError(null);
      await api.delete(`/work-orders/${id}/photos/${photoId}`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al eliminar la foto");
    }
  }

  if (loading) return <div style={{ padding: "2rem", textAlign: "center" }}>Cargando...</div>;
  if (error && !wo) return <div style={{ padding: "1rem", color: theme.danger }}>{error}</div>;
  if (!wo) return <div style={{ padding: "1rem" }}>No encontrado</div>;

  const loc = locations.find(l => l.id === wo.location_id);
  const ast = assets.find(a => a.id === wo.asset_id);
  const cust = customers.find(c => c.person_id === wo.customer_id);
  const at = types.find(t => t.id === wo.work_order_type_id);
  const pri = priorities.find(p => p.id === wo.priority_id);
  const tech = technicians.find(t => t.person_id === wo.technician_id);

  const isOffice = me?.role_code === "TENANT_ADMIN" || me?.role_code === "TENANT_OFFICE";

  return (
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", gap: "0.5rem", flexWrap: "wrap" }}>
        <h1>OT #{wo.number}</h1>
        <div style={{ display: "flex", gap: "0.375rem" }}>
          <PriorityBadge code={wo.priority_code} label={wo.priority_label} />
          <StatusBadge code={wo.status_code} label={wo.status_label} />
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={load} />}

      <dl style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: "0.5rem 1rem", marginBottom: "1.5rem" }}>
        <dt>Cliente</dt><dd>{cust?.display_name || wo.customer_id}</dd>
        <dt>Ubicación</dt><dd>{loc?.name || wo.location_id}</dd>
        <dt>Activo</dt><dd>{ast?.name || wo.asset_id}</dd>
        <dt>Tipo</dt><dd>{at?.label || wo.work_order_type_id}</dd>
        <dt>Prioridad</dt><dd>{pri?.label || wo.priority_id}</dd>
        <dt>Técnico</dt><dd>{tech?.display_name || "Sin asignar"}</dd>
        <dt>Solicitada</dt><dd>{wo.requested_description || "—"}</dd>
        <dt>Realizada</dt><dd>{wo.performed_description || "—"}</dd>
        <dt>Programada</dt><dd>{wo.scheduled_at || "—"}</dd>
        <dt>Iniciada</dt><dd>{wo.started_at || "—"}</dd>
        <dt>Finalizada</dt><dd>{wo.finished_at || "—"}</dd>
      </dl>

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginBottom: "2rem" }}>
        {isOffice && !wo.is_terminal && (
          <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem" }}>
            <h3 style={{ marginTop: 0 }}>Asignar técnico</h3>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <select value={assignTechId} onChange={e => setAssignTechId(e.target.value)} style={{ flex: 1, padding: "0.5rem" }}>
                <option value="">Seleccionar técnico</option>
                {technicians.map(t => (<option key={t.person_id} value={t.person_id}>{t.display_name}</option>))}
              </select>
              <button
                disabled={!assignTechId || actionLoading}
                onClick={() => runAction(() => api.post(`/work-orders/${id}/assign`, { technician_id: assignTechId }))}
                style={{ padding: "0.5rem 1rem", background: theme.primary, color: theme.primaryText, border: "none", borderRadius: "0.375rem", cursor: "pointer" }}
              >
                Asignar
              </button>
            </div>
          </div>
        )}

        {wo.status_code === "PENDING" && (
          <button
            disabled={actionLoading}
            onClick={() => runAction(() => api.post(`/work-orders/${id}/start`, {}))}
            style={{ padding: "1rem", background: theme.primary, color: theme.primaryText, border: "none", borderRadius: "0.5rem", fontSize: "1rem", cursor: "pointer" }}
          >
            Iniciar OT
          </button>
        )}

        {wo.status_code === "IN_PROGRESS" && (
          <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem" }}>
            <h3 style={{ marginTop: 0 }}>Registrar trabajo realizado</h3>
            <textarea
              value={performedDescription}
              onChange={e => setPerformedDescription(e.target.value)}
              rows={3}
              style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", marginBottom: "0.75rem" }}
            />
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              <button
                disabled={!performedDescription.trim() || actionLoading}
                onClick={() => runAction(() => api.post(`/work-orders/${id}/register-work`, { performed_description: performedDescription }))}
                style={{ padding: "0.75rem 1rem", background: theme.bg, color: theme.text, border: "none", borderRadius: "0.375rem", cursor: "pointer" }}
              >
                Guardar avance
              </button>
              <button
                disabled={actionLoading}
                onClick={() => runAction(() => api.post(`/work-orders/${id}/finish`, { status_code: "COMPLETED", performed_description: performedDescription || undefined }))}
                style={{ padding: "0.75rem 1rem", background: theme.successSolid, color: theme.primaryText, border: "none", borderRadius: "0.375rem", cursor: "pointer" }}
              >
                Cerrar como Terminada
              </button>
              <button
                disabled={actionLoading}
                onClick={() => runAction(() => api.post(`/work-orders/${id}/finish`, { status_code: "UNRESOLVED", performed_description: performedDescription || undefined }))}
                style={{ padding: "0.75rem 1rem", background: theme.dangerSolid, color: theme.primaryText, border: "none", borderRadius: "0.375rem", cursor: "pointer" }}
              >
                Cerrar como No resuelta
              </button>
            </div>
          </div>
        )}

        {isOffice && wo.is_terminal && (
          <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem" }}>
            <h3 style={{ marginTop: 0 }}>Reapertura controlada</h3>
            <textarea
              value={reopenNotes}
              onChange={e => setReopenNotes(e.target.value)}
              rows={2}
              placeholder="Motivo de la reapertura (obligatorio)"
              style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", marginBottom: "0.75rem" }}
            />
            <button
              disabled={reopenNotes.trim().length < 3 || actionLoading}
              onClick={() => runAction(() => api.post(`/work-orders/${id}/reopen`, { notes: reopenNotes }))}
              style={{ padding: "0.75rem 1rem", background: theme.warning, color: theme.primaryText, border: "none", borderRadius: "0.375rem", cursor: "pointer" }}
            >
              Reabrir OT
            </button>
          </div>
        )}
      </div>

      <h2>Fotografías</h2>
      <div style={{ marginBottom: "1rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(100px, 1fr))", gap: "0.5rem", marginBottom: "0.75rem" }}>
          {photos.map((p) => (
            <div key={p.id} style={{ position: "relative" }}>
              {photoUrls[p.id] ? (
                <img
                  src={photoUrls[p.id]}
                  alt={p.caption || "Foto de OT"}
                  style={{ width: "100%", height: "100px", objectFit: "cover", borderRadius: "0.5rem", border: `1px solid ${theme.border}` }}
                />
              ) : (
                <div style={{ width: "100%", height: "100px", background: theme.bg, borderRadius: "0.5rem" }} />
              )}
              {!wo.is_terminal && (
                <button
                  onClick={() => handleDeletePhoto(p.id)}
                  title="Eliminar foto"
                  aria-label="Eliminar foto"
                  style={{ position: "absolute", top: "0.25rem", right: "0.25rem", background: "rgba(220,38,38,0.9)", color: theme.primaryText, border: "none", borderRadius: "9999px", width: "1.5rem", height: "1.5rem", cursor: "pointer", lineHeight: 1 }}
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
        {!wo.is_terminal && (
          <label style={{ display: "inline-block", padding: "0.625rem 1rem", background: theme.primary, opacity: uploadingPhoto ? 0.6 : 1, color: theme.primaryText, borderRadius: "0.5rem", cursor: uploadingPhoto ? "not-allowed" : "pointer", fontSize: "0.875rem" }}>
            {uploadingPhoto ? "Subiendo..." : "📷 Tomar / subir foto"}
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handlePhotoSelected}
              disabled={uploadingPhoto}
              style={{ display: "none" }}
            />
          </label>
        )}
      </div>

      <h2>Historial</h2>
      {history.length === 0 ? (
        <p style={{ color: theme.textSecondary }}>Sin eventos.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {history.map(h => (
            <li key={h.id} style={{ borderLeft: `2px solid ${theme.border}`, paddingLeft: "1rem", marginBottom: "0.75rem" }}>
              <div style={{ fontWeight: 600 }}>{h.event_type}</div>
              <div style={{ color: theme.textSecondary, fontSize: "0.875rem" }}>
                {h.previous_value && `${h.previous_value} → `}{h.new_value}
                {" • "}{new Date(h.performed_at).toLocaleString()}
              </div>
              {h.notes && <div style={{ fontSize: "0.875rem", marginTop: "0.25rem" }}>{h.notes}</div>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
