# Estado operativo

## Contexto manual

- Template v2.0.0: activo y vigente.
- Work unit `10-validacion-postgresql`: cerrada y mergeada en `develop` por PR #4.
- Merge: `de04bac5e0f75997b5dcb820536544fd942e0a8a`.
- Alcance completado: reparación reproducible de Alembic y validación
  PostgreSQL/RLS, preservando SQLite y los contratos funcionales.
- PR #2: referencia legacy iniciada antes de Template v2; cerrada como
  superseded después del merge de PR #4, con trazabilidad conservada.
- Estado: ninguna work unit activa; develop listo para el siguiente punto.
- Release: GI-OT continúa pre-release; no existen tags ni releases.

## Fuentes

El bloque automático futuro será derivado de Git/GitHub. Este documento no
reemplaza Git, CI, `ROADMAP.md`, SDD, `runs/` ni `.audit/`.

## Próximo paso

Iniciar únicamente la próxima work unit aprobada del ROADMAP. Punto 11 queda
pendiente y no se inicia como parte del cierre de Punto 10.

<!-- STATUS:AUTO:BEGIN -->
## Estado verificado automáticamente

- Rama: develop
- HEAD: de04bac5e0f75997b5dcb820536544fd942e0a8a
- Release: pre-release
- Work unit: ninguna activa
- PR #4: MERGED
- PR #2: CLOSED / SUPERSEDED
- CI: PASS — governance, producto, PostgreSQL, quality y frontend

<!-- STATUS:AUTO:END -->
