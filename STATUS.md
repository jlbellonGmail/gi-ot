# Estado operativo

## Contexto manual

- Template v2.0.0: activo y vigente.
- Work unit: `10-validacion-postgresql` en `feature/v2-10-validacion-postgresql`.
- Baseline de la work unit: `develop` en `2cb2a1223117bfb127df61fa6cb89cb4132919dd`.
- Alcance: reparación reproducible de Alembic y validación PostgreSQL/RLS,
  preservando SQLite y los contratos funcionales.
- PR #2: referencia legacy iniciada antes de Template v2; intacta y no
  reinterpretada.
- Estado: implementación y CI remoto validados; work unit lista para HITL.
- Release: GI-OT continúa pre-release; no existen tags ni releases.

## Fuentes

El bloque automático futuro será derivado de Git/GitHub. Este documento no
reemplaza Git, CI, `ROADMAP.md`, SDD, `runs/` ni `.audit/`.

## Próximo paso

Mergear la PR v2 tras la autorización HITL ya concedida. No iniciar Punto 11.

<!-- STATUS:AUTO:BEGIN -->
## Estado verificado automáticamente

- Rama: feature/v2-10-validacion-postgresql
- Base: 2cb2a1223117bfb127df61fa6cb89cb4132919dd
- Release: pre-release
- PR: #4 OPEN
- CI: PASS — governance, producto, PostgreSQL, quality y frontend

<!-- STATUS:AUTO:END -->
