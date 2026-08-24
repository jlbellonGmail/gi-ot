"use client";

import { useEffect, useState } from "react";
import { theme } from "@/lib/theme";

export default function TecnicoLayout({ children }: { children: React.ReactNode }) {
  const [authed, setAuthed] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/login"; return; }
    setAuthed(true); setChecking(false);
  }, []);

  if (checking) return <div style={{ padding: "2rem", textAlign: "center", color: theme.textSecondary }}>Cargando...</div>;
  if (!authed) return null;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: theme.bg }}>
      <header style={{ background: theme.headerBg, color: theme.headerText, padding: "0.875rem 1rem", position: "sticky", top: 0, zIndex: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontWeight: 700, fontSize: "1.125rem" }}>gi-ot</span>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {/* Estado estático: la sincronización real (cola/offline) llega en Etapa 08 */}
          <span style={{ fontSize: "0.75rem", color: theme.headerSuccess }}>● Sincronizado</span>
          <button
            onClick={() => { localStorage.removeItem("access_token"); window.location.href = "/login"; }}
            style={{ padding: "0.375rem 0.75rem", background: "transparent", border: "1px solid " + theme.headerActive, color: theme.headerText, borderRadius: "0.375rem", cursor: "pointer", fontSize: "0.8rem" }}
          >
            Salir
          </button>
        </div>
      </header>
      <main style={{ flex: 1, padding: "1rem", maxWidth: "480px", margin: "0 auto", width: "100%", color: theme.text }}>
        {children}
      </main>
    </div>
  );
}
