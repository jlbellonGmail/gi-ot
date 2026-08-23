import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Evita que Turbopack confunda la raíz del workspace con un directorio
  // padre ajeno a gi-ot (hay un pnpm-lock.yaml fuera del proyecto).
  turbopack: {
    root: path.join(__dirname),
  },
  // Permite acceder al servidor de desarrollo desde la IP de la red local
  // (prueba manual desde celular, ROADMAP §06). Solo aplica en `next dev`.
  allowedDevOrigins: ["192.168.0.5"],
};

export default nextConfig;
