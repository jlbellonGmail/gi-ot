"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Technician, TechnicianUpdate, UserAccount } from "@/lib/types";

export default function TechnicianDetailPage() {
  const params = useParams(); const router = useRouter(); const personId = params.id as string;
  const [tech, setTech] = useState<Technician | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);

  const [form, setForm] = useState<TechnicianUpdate>({
    person_type: "INDIVIDUAL", display_name: "", address: "", phone: "", email: "", notes: "",
    status: "ACTIVE", profession: "", license_number: "", commission_percentage: 0, technician_status: "ACTIVE"
  });

  // Vínculo Técnico ↔ Usuario (ROADMAP §06 — necesario para que el
  // técnico pueda loguearse y usar /tecnico). GET /users es solo para
  // TENANT_ADMIN; si el usuario logueado es TENANT_OFFICE la lista
  // queda vacía y se oculta el selector, sin romper la página.
  const [users, setUsers] = useState<UserAccount[]>([]);
  const [canManageUsers, setCanManageUsers] = useState(true);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [linking, setLinking] = useState(false);
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserName, setNewUserName] = useState("");
  const [newUserPassword, setNewUserPassword] = useState("");
  const [creatingUser, setCreatingUser] = useState(false);

  useEffect(() => { load(); loadUsers(); }, [personId]);

  async function load() {
    try {
      setLoading(true);
      const data = await api.get<Technician>(`/technicians/${personId}`);
      setTech(data);
      setForm({ person_type: data.person_type, display_name: data.display_name, address: data.address || "", phone: data.phone || "", email: data.email || "", notes: data.notes || "", status: data.status, profession: data.profession || "", license_number: data.license_number || "", commission_percentage: data.commission_percentage || 0, technician_status: data.technician_status });
    } catch (e) { setError(e instanceof Error ? e.message : "Error al cargar"); }
    finally { setLoading(false); }
  }

  async function loadUsers() {
    try {
      const list = await api.get<UserAccount[]>("/users");
      setUsers(list.filter((u) => u.role_code === "TENANT_TECHNICIAN"));
    } catch {
      setCanManageUsers(false);
    }
  }

  async function save() {
    try { setSaving(true); setError(null); await api.patch(`/technicians/${personId}`, form); await load(); setEditMode(false); }
    catch (e) { setError(e instanceof Error ? e.message : "Error al guardar"); }
    finally { setSaving(false); }
  }

  async function linkUser(userId: string | null) {
    try {
      setLinking(true); setError(null);
      await api.patch(`/technicians/${personId}/user`, { user_id: userId });
      setSelectedUserId("");
      await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Error al vincular usuario"); }
    finally { setLinking(false); }
  }

  async function createAndLinkUser() {
    try {
      setCreatingUser(true); setError(null);
      const user = await api.post<UserAccount>("/users", {
        email: newUserEmail, full_name: newUserName, password: newUserPassword, role_code: "TENANT_TECHNICIAN",
      });
      await api.patch(`/technicians/${personId}/user`, { user_id: user.id });
      setNewUserEmail(""); setNewUserName(""); setNewUserPassword("");
      await loadUsers();
      await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Error al crear/vincular usuario"); }
    finally { setCreatingUser(false); }
  }

  if (loading) return <div style={{ padding: "1rem", textAlign: "center" }}>Cargando...</div>;
  if (error && !tech) return <div style={{ padding: "1rem", color: theme.danger }}>{error}</div>;
  if (!tech) return <div style={{ padding: "1rem" }}>No encontrado</div>;

  return (
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1>{tech.display_name}</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={()=>setEditMode(!editMode)} style={{ padding: "0.5rem 1rem" }}>{editMode?"Cancelar":"Editar"}</button>
          <button onClick={()=>router.back()} style={{ padding: "0.5rem 1rem", background: theme.bg }}>Volver</button>
        </div>
      </div>
      {error && <div style={{ background: theme.dangerBg, color: theme.danger, padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}
      <div style={{ display: "grid", gap: "1rem" }}>
        <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.75rem" }}>Identificaciones</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {tech.identifications.map(i=>(<span key={i.id} style={{ background: i.is_primary?theme.infoBg:theme.bg, color: theme.text, padding: "0.25rem 0.75rem", borderRadius: "9999px", fontSize: "0.875rem" }}>{i.identification_type}: {i.identification_value} {i.is_primary&&"(principal)"}</span>))}
          </div>
        </div>
        <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.75rem" }}>Datos</h3>
          {editMode ? (
            <div style={{ display: "grid", gap: "1rem" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div><label htmlFor="edit-tech-type" style={{ display: "block", marginBottom: "0.25rem" }}>Tipo</label><select id="edit-tech-type" value={form.person_type} onChange={e=>setForm({...form, person_type: e.target.value as "INDIVIDUAL"|"LEGAL"})} style={{ width: "100%", padding: "0.5rem" }}><option value="INDIVIDUAL">Física</option><option value="LEGAL">Jurídica</option></select></div>
                <div><label htmlFor="edit-tech-status" style={{ display: "block", marginBottom: "0.25rem" }}>Estado Persona</label><select id="edit-tech-status" value={form.status} onChange={e=>setForm({...form, status: e.target.value as "ACTIVE"|"INACTIVE"})} style={{ width: "100%", padding: "0.5rem" }}><option value="ACTIVE">Activo</option><option value="INACTIVE">Inactivo</option></select></div>
              </div>
              <div><label htmlFor="edit-tech-name" style={{ display: "block", marginBottom: "0.25rem" }}>Nombre</label><input id="edit-tech-name" value={form.display_name} onChange={e=>setForm({...form, display_name: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} required /></div>
              <div><label htmlFor="edit-tech-address" style={{ display: "block", marginBottom: "0.25rem" }}>Dirección</label><input id="edit-tech-address" value={form.address} onChange={e=>setForm({...form, address: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} /></div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div><label htmlFor="edit-tech-phone" style={{ display: "block", marginBottom: "0.25rem" }}>Teléfono</label><input id="edit-tech-phone" value={form.phone} onChange={e=>setForm({...form, phone: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} /></div>
                <div><label htmlFor="edit-tech-email" style={{ display: "block", marginBottom: "0.25rem" }}>Email</label><input id="edit-tech-email" value={form.email} onChange={e=>setForm({...form, email: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} /></div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" }}>
                <div><label htmlFor="edit-tech-profession" style={{ display: "block", marginBottom: "0.25rem" }}>Profesión</label><input id="edit-tech-profession" value={form.profession} onChange={e=>setForm({...form, profession: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} /></div>
                <div><label htmlFor="edit-tech-license" style={{ display: "block", marginBottom: "0.25rem" }}>Matrícula</label><input id="edit-tech-license" value={form.license_number} onChange={e=>setForm({...form, license_number: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} /></div>
                <div><label htmlFor="edit-tech-commission" style={{ display: "block", marginBottom: "0.25rem" }}>Comisión %</label><input id="edit-tech-commission" type="number" step="0.1" value={form.commission_percentage} onChange={e=>setForm({...form, commission_percentage: parseFloat(e.target.value)||0})} style={{ width: "100%", padding: "0.5rem" }} /></div>
              </div>
              <div><label htmlFor="edit-tech-technician-status" style={{ display: "block", marginBottom: "0.25rem" }}>Estado Técnico</label><select id="edit-tech-technician-status" value={form.technician_status} onChange={e=>setForm({...form, technician_status: e.target.value as "ACTIVE"|"INACTIVE"})} style={{ width: "100%", padding: "0.5rem" }}><option value="ACTIVE">Activo</option><option value="INACTIVE">Inactivo</option></select></div>
              <div><label htmlFor="edit-tech-notes" style={{ display: "block", marginBottom: "0.25rem" }}>Observaciones</label><textarea id="edit-tech-notes" value={form.notes} onChange={e=>setForm({...form, notes: e.target.value})} rows={3} style={{ width: "100%", padding: "0.5rem" }} /></div>
              <div style={{ display: "flex", justifyContent: "flex-end" }}><button onClick={save} disabled={saving} style={{ padding: "0.5rem 1.5rem", background: theme.successSolid, color: theme.primaryText, border: "none", borderRadius: "0.375rem" }}>{saving?"Guardando...":"Guardar"}</button></div>
            </div>
          ) : (
            <dl style={{ display: "grid", gridTemplateColumns: "150px 1fr", gap: "0.5rem 1rem" }}>
              <dt>Tipo</dt><dd>{tech.person_type==="LEGAL"?"Jurídica":"Física"}</dd>
              <dt>Dirección</dt><dd>{tech.address||"—"}</dd>
              <dt>Teléfono</dt><dd>{tech.phone||"—"}</dd>
              <dt>Email</dt><dd>{tech.email||"—"}</dd>
              <dt>Profesión</dt><dd>{tech.profession||"—"}</dd>
              <dt>Matrícula</dt><dd>{tech.license_number||"—"}</dd>
              <dt>Comisión</dt><dd>{tech.commission_percentage}%</dd>
              <dt>Estado Persona</dt><dd><span style={{ background: tech.status==="ACTIVE"?theme.successBg:theme.dangerBg, color: tech.status==="ACTIVE"?theme.success:theme.danger, padding: "0.125rem 0.5rem", borderRadius: "9999px", fontSize: "0.875rem" }}>{tech.status}</span></dd>
              <dt>Estado Técnico</dt><dd><span style={{ background: tech.technician_status==="ACTIVE"?theme.successBg:theme.dangerBg, color: tech.technician_status==="ACTIVE"?theme.success:theme.danger, padding: "0.125rem 0.5rem", borderRadius: "9999px", fontSize: "0.875rem" }}>{tech.technician_status}</span></dd>
              <dt>Observaciones</dt><dd>{tech.notes||"—"}</dd>
            </dl>
          )}
        </div>

        <div style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.75rem" }}>Cuenta de usuario (acceso técnico)</h3>
          {tech.user_id ? (
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>
                Vinculado a: {users.find((u) => u.id === tech.user_id)?.email || tech.user_id}
              </span>
              <button
                onClick={() => linkUser(null)}
                disabled={linking}
                style={{ padding: "0.5rem 1rem", background: theme.dangerBg, color: theme.danger, border: `1px solid ${theme.danger}`, borderRadius: "0.375rem", cursor: "pointer" }}
              >
                Desvincular
              </button>
            </div>
          ) : !canManageUsers ? (
            <p style={{ color: theme.textSecondary, fontSize: "0.875rem" }}>
              Necesitás rol Admin para gestionar usuarios técnicos.
            </p>
          ) : (
            <div style={{ display: "grid", gap: "1rem" }}>
              {users.length > 0 && (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <select value={selectedUserId} onChange={(e) => setSelectedUserId(e.target.value)} style={{ flex: 1, padding: "0.5rem" }}>
                    <option value="">Seleccionar usuario técnico existente</option>
                    {users.map((u) => (<option key={u.id} value={u.id}>{u.full_name} ({u.email})</option>))}
                  </select>
                  <button
                    onClick={() => linkUser(selectedUserId)}
                    disabled={!selectedUserId || linking}
                    style={{ padding: "0.5rem 1rem", background: theme.primary, color: theme.primaryText, border: "none", borderRadius: "0.375rem", cursor: "pointer" }}
                  >
                    Vincular
                  </button>
                </div>
              )}
              <div style={{ borderTop: `1px solid ${theme.border}`, paddingTop: "0.75rem" }}>
                <p style={{ fontSize: "0.875rem", color: theme.textSecondary, marginBottom: "0.5rem" }}>O crear un usuario técnico nuevo y vincularlo:</p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr auto", gap: "0.5rem" }}>
                  <input placeholder="Nombre completo" aria-label="Nombre completo" value={newUserName} onChange={(e) => setNewUserName(e.target.value)} style={{ padding: "0.5rem" }} />
                  <input placeholder="Email" aria-label="Email" type="email" value={newUserEmail} onChange={(e) => setNewUserEmail(e.target.value)} style={{ padding: "0.5rem" }} />
                  <input placeholder="Contraseña" aria-label="Contraseña" type="password" value={newUserPassword} onChange={(e) => setNewUserPassword(e.target.value)} style={{ padding: "0.5rem" }} />
                  <button
                    onClick={createAndLinkUser}
                    disabled={!newUserEmail || !newUserName || !newUserPassword || creatingUser}
                    style={{ padding: "0.5rem 1rem", background: theme.successSolid, color: theme.primaryText, border: "none", borderRadius: "0.375rem", cursor: "pointer" }}
                  >
                    {creatingUser ? "Creando..." : "Crear y vincular"}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}