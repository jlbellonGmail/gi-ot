"use client";

import { useEffect } from "react";

// Registro del Service Worker mínimo passthrough (ver public/service-worker.js).
// El cacheo real / soporte offline llega en la Etapa 07 del ROADMAP.
export default function ServiceWorkerRegister() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/service-worker.js").catch((err) => {
        console.error("No se pudo registrar el Service Worker", err);
      });
    }
  }, []);

  return null;
}
