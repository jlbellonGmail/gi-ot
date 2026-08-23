"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Customer, CustomerUpdate } from "@/lib/types";

export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const personId = params.id as string;

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);

  const [formData, setFormData] = useState<CustomerUpdate>({
    person_type: "INDIVIDUAL",
    display_name: "",
    address: "",
    phone: "",
    email: "",
    notes: "",
    status: "ACTIVE",
  });

  useEffect(() => {
    loadCustomer();
  }, [personId]);

  async function loadCustomer() {
    try {
      setLoading(true);
      const data = await api.get<Customer>(`/customers/${personId}`);
      setCustomer(data);
      setFormData({
        person_type: data.person_type,
        display_name: data.display_name,
        address: data.address || "",
        phone: data.phone || "",
        email: data.email || "",
        notes: data.notes || "",
        status: data.status,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar cliente");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    try {
      setSaving(true);
      setError(null);
      await api.patch(`/customers/${personId}`, formData);
      await loadCustomer();
      setEditMode(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div style={{ padding: "1rem", textAlign: "center" }}>Cargando...</div>;
  if (error && !customer) return <div style={{ padding: "1rem", color: "red" }}>{error}</div>;
  if (!customer) return <div style={{ padding: "1rem" }}>Cliente no encontrado</div>;

  return (
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1>{customer.display_name}</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={() => setEditMode(!editMode)} style={{ padding: "0.5rem 1rem" }}>
            {editMode ? "Cancelar" : "Editar"}
          </button>
          <button onClick={() => router.back()} style={{ padding: "0.5rem 1rem", background: "#f3f4f6" }}>
            Volver
          </button>
        </div>
      </div>

      {error && <div style={{ background: "#fef2f2", color: "#dc2626", padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>{error}</div>}

      <div style={{ display: "grid", gap: "1rem" }}>
        <div style={{ border: "1px solid #e5e7eb", borderRadius: "0.5rem", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.75rem" }}>Identificaciones</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {customer.identifications.map((ident) => (
              <span key={ident.id} style={{
                background: ident.is_primary ? "#dbeafe" : "#f3f4f6",
                color: ident.is_primary ? "#1d4ed8" : "#374151",
                padding: "0.25rem 0.75rem",
                borderRadius: "9999px",
                fontSize: "0.875rem",
                border: ident.is_primary ? "1px solid #3b82f6" : "none",
              }}>
                {ident.identification_type}: {ident.identification_value} {ident.is_primary && "(principal)"}
              </span>
            ))}
          </div>
        </div>

        <div style={{ border: "1px solid #e5e7eb", borderRadius: "0.5rem", padding: "1rem" }}>
          <h3 style={{ marginBottom: "0.75rem" }}>Datos de contacto</h3>
          {editMode ? (
            <div style={{ display: "grid", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 500 }}>Tipo persona</label>
                <select value={formData.person_type} onChange={(e) => setFormData({...formData, person_type: e.target.value as "INDIVIDUAL" | "LEGAL"})} style={{ width: "100%", padding: "0.5rem" }}>
                  <option value="INDIVIDUAL">Física</option>
                  <option value="LEGAL">Jurídica</option>
                </select>
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 500 }}>Nombre / Razón social</label>
                <input value={formData.display_name} onChange={(e) => setFormData({...formData, display_name: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} required />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 500 }}>Dirección</label>
                <input value={formData.address} onChange={(e) => setFormData({...formData, address: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div>
                  <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 500 }}>Teléfono</label>
                  <input value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} />
                </div>
                <div>
                  <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 500 }}>Email</label>
                  <input value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} style={{ width: "100%", padding: "0.5rem" }} />
                </div>
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 500 }}>Estado</label>
                <select value={formData.status} onChange={(e) => setFormData({...formData, status: e.target.value as "ACTIVE" | "INACTIVE"})} style={{ width: "100%", padding: "0.5rem" }}>
                  <option value="ACTIVE">Activo</option>
                  <option value="INACTIVE">Inactivo</option>
                </select>
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "0.25rem", fontWeight: 500 }}>Observaciones</label>
                <textarea value={formData.notes} onChange={(e) => setFormData({...formData, notes: e.target.value})} rows={3} style={{ width: "100%", padding: "0.5rem" }} />
              </div>
              <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
                <button onClick={handleSave} disabled={saving} style={{ padding: "0.5rem 1.5rem", background: "#2563eb", color: "white", border: "none", borderRadius: "0.375rem" }}>
                  {saving ? "Guardando..." : "Guardar"}
                </button>
              </div>
            </div>
          ) : (
            <dl style={{ display: "grid", gridTemplateColumns: "150px 1fr", gap: "0.5rem 1rem" }}>
              <dt>Tipo</dt><dd>{customer.person_type === "LEGAL" ? "Jurídica" : "Física"}</dd>
              <dt>Dirección</dt><dd>{customer.address || "—"}</dd>
              <dt>Teléfono</dt><dd>{customer.phone || "—"}</dd>
              <dt>Email</dt><dd>{customer.email || "—"}</dd>
              <dt>Estado</dt><dd><span style={{ background: customer.status === "ACTIVE" ? "#dcfce7" : "#fef2f2", color: customer.status === "ACTIVE" ? "#166534" : "#dc2626", padding: "0.125rem 0.5rem", borderRadius: "9999px", fontSize: "0.875rem" }}>{customer.status}</span></dd>
              <dt>Observaciones</dt><dd>{customer.notes || "—"}</dd>
            </dl>
          )}
        </div>
      </div>
    </div>
  );
}