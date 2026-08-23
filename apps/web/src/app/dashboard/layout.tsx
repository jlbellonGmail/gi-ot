"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { theme } from "@/lib/theme";

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
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/login"; return; }
    setAuthed(true); setChecking(false);
  }, []);

  // El nav mobile se cierra solo al cambiar de ruta, para no quedar
  // abierto tapando la pantalla siguiente.
  useEffect(() => { setMenuOpen(false); }, [pathname]);

  if (checking) return <div style={{ padding: "2rem", textAlign: "center", color: theme.textSecondary }}>Cargando...</div>;
  if (!authed) return null;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: theme.bg }}>
      <header style={{ background: theme.headerBg, color: theme.headerText, padding: "0.75rem 1rem", position: "sticky", top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto", position: "relative", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Link href="/dashboard" style={{ fontWeight: 700, fontSize: "1.25rem", color: theme.headerText, textDecoration: "none" }}>gi-ot</Link>

          <button
            onClick={() => setMenuOpen((v) => !v)}
            aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
            aria-expanded={menuOpen}
            className="dashboard-nav-toggle"
            style={{ background: "transparent", border: "1px solid " + theme.headerActive, color: theme.headerText, borderRadius: "0.375rem", padding: "0.5rem 0.75rem", fontSize: "1rem", cursor: "pointer", alignItems: "center", justifyContent: "center" }}
          >
            {menuOpen ? "✕" : "☰"}
          </button>

          <nav className={`dashboard-nav${menuOpen ? " open" : ""}`}>
            {navItems.map(item => (
              <Link key={item.href} href={item.href} style={{
                padding: "0.5rem 1rem", borderRadius: "0.375rem",
                background: pathname.startsWith(item.href) ? theme.headerActive : "transparent",
                color: theme.headerText, textDecoration: "none", fontSize: "0.875rem", display: "flex", alignItems: "center", gap: "0.375rem"
              }}>
                {item.icon} {item.label}
              </Link>
            ))}
            <button onClick={() => { localStorage.removeItem("access_token"); window.location.href = "/login"; }}
              style={{ padding: "0.5rem 1rem", background: "transparent", border: "1px solid " + theme.headerActive, color: theme.headerText, borderRadius: "0.375rem", cursor: "pointer" }}>
              Salir
            </button>
          </nav>
        </div>
      </header>
      <main style={{ flex: 1, padding: "1rem", maxWidth: "1200px", margin: "0 auto", width: "100%", color: theme.text }}>
        {children}
      </main>
    </div>
  );
}
