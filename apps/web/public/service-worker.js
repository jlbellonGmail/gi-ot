// Service Worker mínimo passthrough — habilita la instalabilidad de la PWA
// (ROADMAP §06). No cachea nada: el cacheo real / soporte offline se
// implementa en la Etapa 07 (Offline y sincronización).
self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", () => {
  // Passthrough: no intercepta la respuesta de red.
});
