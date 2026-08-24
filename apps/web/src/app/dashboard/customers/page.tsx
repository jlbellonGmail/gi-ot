"use client";

import { theme } from "@/lib/theme";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Customer } from "@/lib/types";

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadCustomers() {
    try {
      setLoading(true);
      const data = await api.get<Customer[]>("/customers");
      setCustomers(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar clientes");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCustomers();
  }, []);

  return (
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1>Clientes</h1>
        <Link href="/dashboard/customers/new" style={{ textDecoration: "none" }}>
          <button style={{
            background: theme.primary,
            color: theme.primaryText,
            border: "none",
            padding: "0.75rem 1.5rem",
            borderRadius: "0.5rem",
            fontSize: "1rem",
            cursor: "pointer",
          }}>
            + Nuevo Cliente
          </button>
        </Link>
      </div>

      {error && (
        <div style={{ background: theme.dangerBg, border: `1px solid ${theme.danger}`, color: theme.danger, padding: "1rem", borderRadius: "0.5rem", marginBottom: "1rem" }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: "2rem" }}>Cargando...</div>
      ) : customers.length === 0 ? (
        <div style={{ textAlign: "center", padding: "2rem", color: theme.textSecondary }}>
          No hay clientes registrados.
          <br />
          <Link href="/dashboard/customers/new">Crear el primero</Link>
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {customers.map((c) => (
            <li key={c.person_id} style={{
              border: `1px solid ${theme.border}`,
              borderRadius: "0.5rem",
              padding: "1rem",
              marginBottom: "0.75rem",
              background: theme.surface,
            }}>
              <Link href={`/dashboard/customers/${c.person_id}`} style={{ textDecoration: "none", color: "inherit" }}>
                <div style={{ fontWeight: 600, fontSize: "1.1rem" }}>{c.display_name}</div>
                <div style={{ color: theme.textSecondary, fontSize: "0.875rem", marginTop: "0.25rem" }}>
                  {c.person_type === "LEGAL" ? "Persona Jurídica" : "Persona Física"}
                  {c.email && ` • ${c.email}`}
                  {c.phone && ` • ${c.phone}`}
                </div>
                <div style={{ marginTop: "0.5rem", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                  {c.identifications.map((ident) => (
                    <span key={ident.id} style={{
                      background: theme.infoBg,
                      color: theme.primary,
                      padding: "0.25rem 0.5rem",
                      borderRadius: "0.25rem",
                      fontSize: "0.75rem",
                    }}>
                      {ident.identification_type}: {ident.identification_value}
                    </span>
                  ))}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}