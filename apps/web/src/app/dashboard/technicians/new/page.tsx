"use client";

import { theme } from "@/lib/theme";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Disclosure } from "@/components/Disclosure";
import { TechnicianCreate } from "@/lib/types";

const COUNTRIES = [
  { code: "AR", name: "Argentina" }, { code: "UY", name: "Uruguay" },
  { code: "CL", name: "Chile" }, { code: "PE", name: "Perú" },
  { code: "CO", name: "Colombia" }, { code: "MX", name: "México" },
  { code: "ES", name: "España" },
];

const ID_TYPES_BY_COUNTRY: Record<string, string[]> = {
  AR: ["DNI", "CUIT", "CUIL", "Pasaporte"], UY: ["CI", "RUT", "Pasaporte"],
  CL: ["RUT", "Pasaporte"], PE: ["DNI", "RUC", "Pasaporte"],
  CO: ["CC", "NIT", "Pasaporte"], MX: ["RFC", "CURP", "Pasaporte"],
  ES: ["DNI", "NIE", "CIF", "Pasaporte"],
};

export default function NewTechnicianPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<TechnicianCreate>({
    person_type: "INDIVIDUAL",
    display_name: "",
    address: "", phone: "", email: "", notes: "",
    identifications: [{ country_code: "AR", identification_type: "DNI", identification_value: "", is_primary: true }],
    profession: "", license_number: "", commission_percentage: 0,
  });

  const handleChange = (field: keyof TechnicianCreate, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleIdentChange = (idx: number, field: string, value: string) => {
    setFormData((prev) => {
      const ids = [...prev.identifications];
      ids[idx] = { ...ids[idx], [field]: value };
      return { ...prev, identifications: ids };
    });
  };

  const addIdent = () => setFormData((p) => ({ ...p, identifications: [...p.identifications, { country_code: "AR", identification_type: "DNI", identification_value: "", is_primary: false }] }));
  const removeIdent = (idx: number) => setFormData((p) => ({ ...p, identifications: p.identifications.filter((_, i) => i !== idx) }));

  const handleCountryChange = (idx: number, code: string) => {
    const types = ID_TYPES_BY_COUNTRY[code] || ["Otro"];
    setFormData((p) => { const ids = [...p.identifications]; ids[idx] = { ...ids[idx], country_code: code, identification_type: types[0] }; return { ...p, identifications: ids }; });
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null); setLoading(true);
    try {
      const payload = { ...formData, identifications: formData.identifications.map(i => ({ country_code: i.country_code, identification_type: i.identification_type, identification_value: i.identification_value, is_primary: i.is_primary })) };
      const res = await api.post<{ person_id: string }>("/technicians", payload);
      router.push(`/dashboard/technicians/${res.person_id}`); router.refresh();
    } catch (e) { setError(e instanceof Error ? e.message : "Error al crear técnico"); }
    finally { setLoading(false); }
  }

  const idTypes = ID_TYPES_BY_COUNTRY[formData.identifications[0]?.country_code || "AR"] || ["Otro"];

  return (
    <div style={{ padding: "1rem", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Nuevo Técnico</h1>
      <p style={{ color: theme.textSecondary, marginBottom: "1.5rem" }}>Ingrese identificación para verificar si la persona ya existe.</p>
      {error && <ErrorBanner message={error} />}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Tipo persona</label>
          <div style={{ display: "flex", gap: "1rem" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <input type="radio" name="pt" value="INDIVIDUAL" checked={formData.person_type==="INDIVIDUAL"} onChange={()=>handleChange("person_type","INDIVIDUAL")} /> Física
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <input type="radio" name="pt" value="LEGAL" checked={formData.person_type==="LEGAL"} onChange={()=>handleChange("person_type","LEGAL")} /> Jurídica
            </label>
          </div>
        </div>
        <fieldset style={{ border: `1px solid ${theme.border}`, borderRadius: "0.5rem", padding: "1rem", marginBottom: "1rem" }}>
          <legend style={{ fontWeight: 600, marginBottom: "0.5rem" }}>Identificación</legend>
          {formData.identifications.map((ident, idx) => (
            <div key={idx} style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "0.5rem", alignItems: "flex-end" }}>
              <select aria-label="País" value={ident.country_code} onChange={e=>handleCountryChange(idx,e.target.value)} style={{ padding: "0.5rem", minWidth: "120px" }}>
                {COUNTRIES.map(c=><option key={c.code} value={c.code}>{c.name}</option>)}
              </select>
              <select aria-label="Tipo de identificación" value={ident.identification_type} onChange={e=>handleIdentChange(idx,"identification_type",e.target.value)} style={{ padding: "0.5rem", minWidth: "140px" }}>
                {idTypes.map(t=><option key={t} value={t}>{t}</option>)}
              </select>
              <input type="text" placeholder="Número" aria-label="Número de identificación" value={ident.identification_value} onChange={e=>handleIdentChange(idx,"identification_value",e.target.value)} style={{ flex: 1, minWidth: "150px", padding: "0.5rem" }} />
              <label style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                <input type="checkbox" checked={ident.is_primary} onChange={e=>handleIdentChange(idx,"is_primary",e.target.checked?"true":"false")} /> Principal
              </label>
              {formData.identifications.length>1 && <button type="button" onClick={()=>removeIdent(idx)} aria-label="Quitar identificación" style={{ padding: "0.5rem", background: theme.dangerBg, color: theme.danger, border: "none", borderRadius: "0.375rem" }}>×</button>}
            </div>
          ))}
          {formData.identifications.length<3 && <button type="button" onClick={addIdent} style={{ padding: "0.5rem 1rem", background: theme.bg, border: `1px dashed ${theme.border}`, borderRadius: "0.375rem" }}>+ Agregar identificación</button>}
        </fieldset>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="tech-name" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Nombre *</label>
          <input id="tech-name" value={formData.display_name} onChange={e=>handleChange("display_name",e.target.value)} required style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        <Disclosure label="Más datos (dirección, contacto, datos profesionales, observaciones)">
        <div>
          <label htmlFor="tech-address" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Dirección</label>
          <input id="tech-address" value={formData.address} onChange={e=>handleChange("address",e.target.value)} style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div><label htmlFor="tech-phone" style={{ display: "block", marginBottom: "0.25rem" }}>Teléfono</label><input id="tech-phone" value={formData.phone} onChange={e=>handleChange("phone",e.target.value)} style={{ width: "100%", padding: "0.75rem" }} /></div>
          <div><label htmlFor="tech-email" style={{ display: "block", marginBottom: "0.25rem" }}>Email</label><input id="tech-email" value={formData.email} onChange={e=>handleChange("email",e.target.value)} style={{ width: "100%", padding: "0.75rem" }} /></div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" }}>
          <div><label htmlFor="tech-profession" style={{ display: "block", marginBottom: "0.25rem" }}>Profesión</label><input id="tech-profession" value={formData.profession} onChange={e=>handleChange("profession",e.target.value)} style={{ width: "100%", padding: "0.75rem" }} /></div>
          <div><label htmlFor="tech-license" style={{ display: "block", marginBottom: "0.25rem" }}>Matrícula</label><input id="tech-license" value={formData.license_number} onChange={e=>handleChange("license_number",e.target.value)} style={{ width: "100%", padding: "0.75rem" }} /></div>
          <div><label htmlFor="tech-commission" style={{ display: "block", marginBottom: "0.25rem" }}>Comisión %</label><input id="tech-commission" type="number" step="0.1" value={formData.commission_percentage} onChange={e=>handleChange("commission_percentage",parseFloat(e.target.value)||0)} style={{ width: "100%", padding: "0.75rem" }} /></div>
        </div>
        <div>
          <label htmlFor="tech-notes" style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Observaciones</label>
          <textarea id="tech-notes" value={formData.notes} onChange={e=>handleChange("notes",e.target.value)} rows={3} style={{ width: "100%", padding: "0.75rem" }} />
        </div>
        </Disclosure>
        <div style={{ display: "flex", gap: "1rem" }}>
          <button type="submit" disabled={loading} style={{ flex: 1, padding: "1rem", background: theme.successSolid, opacity: loading ? 0.6 : 1, color: theme.primaryText, border: "none", borderRadius: "0.5rem" }}>{loading?"Guardando...":"Crear Técnico"}</button>
          <Link href="/dashboard/technicians" style={{ flex: 1, padding: "1rem", background: theme.bg, textAlign: "center", textDecoration: "none", borderRadius: "0.5rem" }}>Cancelar</Link>
        </div>
      </form>
    </div>
  );
}