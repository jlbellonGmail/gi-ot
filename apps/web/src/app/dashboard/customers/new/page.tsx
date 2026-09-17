"use client";

import { theme } from "@/lib/theme";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Disclosure } from "@/components/Disclosure";
import { CustomerCreate } from "@/lib/types";

const COUNTRIES = [
  { code: "AR", name: "Argentina" },
  { code: "UY", name: "Uruguay" },
  { code: "CL", name: "Chile" },
  { code: "PE", name: "Perú" },
  { code: "CO", name: "Colombia" },
  { code: "MX", name: "México" },
  { code: "ES", name: "España" },
];

const ID_TYPES_BY_COUNTRY: Record<string, string[]> = {
  AR: ["DNI", "CUIT", "CUIL", "Pasaporte"],
  UY: ["CI", "RUT", "Pasaporte"],
  CL: ["RUT", "Pasaporte"],
  PE: ["DNI", "RUC", "Pasaporte"],
  CO: ["CC", "NIT", "Pasaporte"],
  MX: ["RFC", "CURP", "Pasaporte"],
  ES: ["DNI", "NIE", "CIF", "Pasaporte"],
};

export default function NewCustomerPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [personExists, setPersonExists] = useState(false);
  const [existingPersonData, setExistingPersonData] = useState<Partial<CustomerCreate> | null>(null);

  const [formData, setFormData] = useState<CustomerCreate>({
    person_type: "INDIVIDUAL",
    display_name: "",
    address: "",
    phone: "",
    email: "",
    notes: "",
    identifications: [{ country_code: "AR", identification_type: "DNI", identification_value: "", is_primary: true }],
  });

  const handleChange = (field: keyof CustomerCreate, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleIdentificationChange = (index: number, field: string, value: string) => {
    setFormData((prev) => {
      const newIdents = [...prev.identifications];
      newIdents[index] = { ...newIdents[index], [field]: value };
      return { ...prev, identifications: newIdents };
    });
  };

  const addIdentification = () => {
    setFormData((prev) => ({
      ...prev,
      identifications: [...prev.identifications, { country_code: "AR", identification_type: "DNI", identification_value: "", is_primary: false }],
    }));
  };

  const removeIdentification = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      identifications: prev.identifications.filter((_, i) => i !== index),
    }));
  };

  const handlePersonTypeChange = (type: "INDIVIDUAL" | "LEGAL") => {
    setFormData((prev) => ({ ...prev, person_type: type }));
  };

  const handleCountryChange = (index: number, countryCode: string) => {
    const types = ID_TYPES_BY_COUNTRY[countryCode] || ["Otro"];
    setFormData((prev) => {
      const newIdents = [...prev.identifications];
      newIdents[index] = { ...newIdents[index], country_code: countryCode, identification_type: types[0] };
      return { ...prev, identifications: newIdents };
    });
  };

  async function checkExistingPerson() {
    const primaryIdent = formData.identifications[0];
    if (!primaryIdent.identification_value.trim()) return;

    setLoading(true);
    setError(null);
    try {
      // Buscar si existe una persona con esa identificación
      // El backend maneja esto internamente al crear, pero podemos verificar
      // En este MVP, el endpoint de creación ya maneja la lógica de reutilización
      // Mostramos un indicador visual
      setPersonExists(false); // El backend nos dirá
    } catch (e) {
      // Ignorar errores de búsqueda previa
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const payload: CustomerCreate = {
        ...formData,
        identifications: formData.identifications.map((i) => ({
          country_code: i.country_code,
          identification_type: i.identification_type,
          identification_value: i.identification_value,
          is_primary: i.is_primary,
        })),
      };

      const response = await api.post<{ person_id: string }>("/customers", payload);
      router.push(`/dashboard/customers/${response.person_id}`);
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al crear cliente");
    } finally {
      setLoading(false);
    }
  }

  const identificationTypes = ID_TYPES_BY_COUNTRY[formData.identifications[0]?.country_code || "AR"] || ["Otro"];

  return (
    <div style={{ padding: "1rem", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Nuevo Cliente</h1>
      <p style={{ color: theme.textSecondary, marginBottom: "1.5rem" }}>
        Ingrese la identificación para verificar si la persona ya existe.
      </p>

      {error && <ErrorBanner message={error} />}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>
            Tipo de persona
          </label>
          <div style={{ display: "flex", gap: "1rem" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
              <input
                type="radio"
                name="person_type"
                value="INDIVIDUAL"
                checked={formData.person_type === "INDIVIDUAL"}
                onChange={() => handlePersonTypeChange("INDIVIDUAL")}
              />
              Física
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
              <input
                type="radio"
                name="person_type"
                value="LEGAL"
                checked={formData.person_type === "LEGAL"}
                onChange={() => handlePersonTypeChange("LEGAL")}
              />
              Jurídica
            </label>
          </div>
        </div>

        <fieldset style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem", marginBottom: "1rem" }}>
          <legend style={{ fontWeight: 600, marginBottom: "0.5rem" }}>Identificación</legend>
          {formData.identifications.map((ident, idx) => (
            <div key={idx} style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "0.5rem", alignItems: "flex-end" }}>
              <select
                aria-label="País"
                value={ident.country_code}
                onChange={(e) => handleCountryChange(idx, e.target.value)}
                style={{ padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", minWidth: "120px" }}
              >
                {COUNTRIES.map((c) => (
                  <option key={c.code} value={c.code}>{c.name}</option>
                ))}
              </select>
              <select
                aria-label="Tipo de identificación"
                value={ident.identification_type}
                onChange={(e) => handleIdentificationChange(idx, "identification_type", e.target.value)}
                style={{ padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", minWidth: "140px" }}
              >
                {identificationTypes.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Número"
                aria-label="Número de identificación"
                value={ident.identification_value}
                onChange={(e) => handleIdentificationChange(idx, "identification_value", e.target.value)}
                style={{ flex: 1, minWidth: "150px", padding: "0.5rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem" }}
              />
              <label style={{ display: "flex", alignItems: "center", gap: "0.25rem", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={ident.is_primary}
                  onChange={(e) => handleIdentificationChange(idx, "is_primary", e.target.checked ? "true" : "false")}
                />
                Principal
              </label>
              {formData.identifications.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeIdentification(idx)}
                  style={{ padding: "0.5rem", background: theme.dangerBg, color: theme.danger, border: "none", borderRadius: "0.375rem", cursor: "pointer" }}
                >
                  ×
                </button>
              )}
            </div>
          ))}
          {formData.identifications.length < 3 && (
            <button type="button" onClick={addIdentification} style={{ padding: "0.5rem 1rem", background: theme.bg, border: `1px dashed ${theme.border}`, borderRadius: "0.375rem", cursor: "pointer" }}>
              + Agregar otra identificación
            </button>
          )}
        </fieldset>

        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="customer-name" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Nombre / Razón social *</label>
          <input
            id="customer-name"
            type="text"
            value={formData.display_name}
            onChange={(e) => handleChange("display_name", e.target.value)}
            required
            style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", fontSize: "1rem" }}
          />
        </div>

        <Disclosure label="Más datos (dirección, contacto, observaciones)">
        <div>
          <label htmlFor="customer-address" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Dirección</label>
          <input
            id="customer-address"
            type="text"
            value={formData.address || ""}
            onChange={(e) => handleChange("address", e.target.value)}
            style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", fontSize: "1rem" }}
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div>
            <label htmlFor="customer-phone" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Teléfono</label>
            <input
              id="customer-phone"
              type="tel"
              value={formData.phone || ""}
              onChange={(e) => handleChange("phone", e.target.value)}
              style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", fontSize: "1rem" }}
            />
          </div>
          <div>
            <label htmlFor="customer-email" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Email</label>
            <input
              id="customer-email"
              type="email"
              value={formData.email || ""}
              onChange={(e) => handleChange("email", e.target.value)}
              style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", fontSize: "1rem" }}
            />
          </div>
        </div>

        <div>
          <label htmlFor="customer-notes" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Observaciones</label>
          <textarea
            id="customer-notes"
            value={formData.notes || ""}
            onChange={(e) => handleChange("notes", e.target.value)}
            rows={3}
            style={{ width: "100%", padding: "0.75rem", border: `1px solid ${theme.border}`, borderRadius: "0.375rem", fontSize: "1rem" }}
          />
        </div>
        </Disclosure>

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
            {loading ? "Guardando..." : "Crear Cliente"}
          </button>
          <Link
            href="/dashboard/customers"
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