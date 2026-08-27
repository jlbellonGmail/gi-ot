import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ServiceWorkerRegister from "./service-worker-register";
import { OfflineStatusBanner } from "@/app/offline-status-banner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Metadata PWA / mobile-first mínima (docs/tecnica/stack.md, PRD §61).
// Se registra un Service Worker mínimo passthrough (ver service-worker-register.tsx)
// solo para habilitar la instalación; el cacheo offline real llega en la Etapa 07.
export const metadata: Metadata = {
  title: "gi-ot",
  description: "Plataforma SaaS de gestión de Órdenes de Trabajo",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "gi-ot",
  },
  icons: {
    apple: "/icons/icon-192.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#0f172a",
};

// Aplica el tema guardado (si el usuario eligió uno manualmente con
// ThemeToggle.tsx) antes del primer pintado, para evitar el parpadeo
// de ver el tema del sistema por una fracción de segundo y luego saltar
// al elegido. Corre inline y de forma síncrona a propósito.
const themeInitScript = `
(function () {
  try {
    var t = localStorage.getItem("gi-ot-theme");
    if (t === "light" || t === "dark") {
      document.documentElement.setAttribute("data-theme", t);
    }
  } catch (e) {}
})();
`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es" className={`${geistSans.variable} ${geistMono.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body>
        <ServiceWorkerRegister />
        <OfflineStatusBanner />
        {children}
      </body>
    </html>
  );
}
