"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, login } from "@/lib/api";
import { CurrentUser } from "@/lib/types";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null); setLoading(true);
    try {
      await login(email, password);
      const me = await api.get<CurrentUser>("/auth/me");
      router.push(me.role_code === "TENANT_TECHNICIAN" ? "/tecnico" : "/dashboard");
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de login");
    } finally { setLoading(false); }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem", background: "#f8fafc" }}>
      <div style={{ width: "100%", maxWidth: "400px", background: "white", borderRadius: "1rem", padding: "2rem", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }}>
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: 700, color: "#0f172a" }}>gi-ot</h1>
          <p style={{ color: "#6b7280", marginTop: "0.5rem" }}>Iniciar sesión</p>
        </div>

        {error && <div style={{ background: "#fef2f2", color: "#dc2626", padding: "0.75rem", borderRadius: "0.5rem", marginBottom: "1rem", fontSize: "0.875rem" }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Email</label>
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} required autoComplete="email"
              style={{ width: "100%", padding: "0.75rem", border: "1px solid #d1d5db", borderRadius: "0.5rem", fontSize: "1rem" }} />
          </div>
          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Contraseña</label>
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} required autoComplete="current-password"
              style={{ width: "100%", padding: "0.75rem", border: "1px solid #d1d5db", borderRadius: "0.5rem", fontSize: "1rem" }} />
          </div>
          <button type="submit" disabled={loading} style={{ width: "100%", padding: "0.875rem", background: loading?"#93c5fd":"#2563eb", color: "white", border: "none", borderRadius: "0.5rem", fontSize: "1rem", fontWeight: 600, cursor: loading?"not-allowed":"pointer" }}>
            {loading?"Entrando...":"Entrar"}
          </button>
        </form>

        <div style={{ marginTop: "1.5rem", paddingTop: "1.5rem", borderTop: "1px solid #e5e7eb", textAlign: "center", color: "#6b7280", fontSize: "0.875rem" }}>
          Demo: <code>admin@stc.com.ar</code> / <code>AdminA123!</code>
        </div>
      </div>
    </div>
  );
}