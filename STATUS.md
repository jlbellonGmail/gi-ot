# Estado operativo

## Contexto manual

- Template v2.0.0: activo y vigente.
- Versión objetivo: `v0.1.0` pre-release, primer baseline formal de desarrollo.
- Work unit `10-validacion-postgresql`: cerrada y mergeada en `develop` por PR #4.
- Merge: `de04bac5e0f75997b5dcb820536544fd942e0a8a`.
- Alcance completado: reparación reproducible de Alembic y validación
  PostgreSQL/RLS, preservando SQLite y los contratos funcionales.
- PR #2: referencia legacy iniciada antes de Template v2; cerrada como
  superseded después del merge de PR #4, con trazabilidad conservada.
- Estado: ninguna work unit activa; develop listo para el siguiente punto.
- Release: GI-OT continúa pre-release; `v0.1.0` pendiente de publicación tras
  la PR de release `develop → main`.

## Fuentes

El bloque automático futuro será derivado de Git/GitHub. Este documento no
reemplaza Git, CI, `ROADMAP.md`, SDD, `runs/` ni `.audit/`.

## Próximo paso

Iniciar únicamente la próxima work unit aprobada del ROADMAP. Punto 11 queda
pendiente y no se inicia como parte del cierre de Punto 10.

<!-- STATUS:AUTO:BEGIN -->
## Estado verificado automáticamente

- Rama: develop
- HEAD: 0e8535ae9b80d4603bfee0a412075ca9b0fa85ff
- Release: v0.1.0 pre-release (pendiente de publicación)
- Work unit: ninguna activa
- PR #4: MERGED
- PR #2: CLOSED / SUPERSEDED
- CI: PASS — governance, producto, PostgreSQL, quality y frontend

<!-- STATUS:AUTO:END -->
