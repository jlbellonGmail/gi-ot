"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";

const navItems = [
  { href: "/dashboard/ot", label: "Órdenes de Trabajo", icon: "🧾" },
  { href: "/dashboard/customers", label: "Clientes", icon: "👥" },
  { href: "/dashboard/technicians", label: "Técnicos", icon: "🔧" },
  { href: "/dashboard/locations", label: "Ubicaciones", icon: "📍" },
  { href: "/dashboard/assets", label: "Activos", icon: "⚙️" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [authed, setAuthed] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/login"; return; }
    setAuthed(true); setChecking(false);
  }, []);

  if (checking) return <div style={{ padding: "2rem", textAlign: "center" }}>Cargando...</div>;
  if (!authed) return null;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header style={{ background: "#0f172a", color: "white", padding: "0.75rem 1rem", position: "sticky", top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Link href="/dashboard" style={{ fontWeight: 700, fontSize: "1.25rem", color: "white", textDecoration: "none" }}>gi-ot</Link>
          <nav style={{ display: "flex", gap: "0.5rem" }}>
            {navItems.map(item => (
              <Link key={item.href} href={item.href} style={{
                padding: "0.5rem 1rem", borderRadius: "0.375rem",
                background: pathname.startsWith(item.href) ? "#2563eb" : "transparent",
                color: "white", textDecoration: "none", fontSize: "0.875rem", display: "flex", alignItems: "center", gap: "0.375rem"
              }}>
                {item.icon} {item.label}
              </Link>
            ))}
            <button onClick={() => { localStorage.removeItem("access_token"); window.location.href = "/login"; }}
              style={{ padding: "0.5rem 1rem", background: "transparent", border: "1px solid #3b82f6", color: "#93c5fd", borderRadius: "0.375rem", cursor: "pointer" }}>
              Salir
            </button>
          </nav>
        </div>
      </header>
      <main style={{ flex: 1, padding: "1rem", maxWidth: "1200px", margin: "0 auto", width: "100%" }}>
        {children}
      </main>
    </div>
  );
}