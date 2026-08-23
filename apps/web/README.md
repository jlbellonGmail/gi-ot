# gi-ot Web

Next.js + React + TypeScript, PWA/mobile-first. Ver `docs/producto/wireframes.md` y `docs/tecnica/arquitectura.md` en la raíz del proyecto.

Estado actual: esqueleto base (Etapa 01 — Fundación SaaS). Las pantallas funcionales se implementan en etapas posteriores del ROADMAP.

## Desarrollo local

```bash
npm install
cp .env.example .env.local
npm run dev
```

Disponible en `http://localhost:3000`. Requiere la API (`apps/api`) corriendo en `NEXT_PUBLIC_API_URL`.
