# GI-OT

GI-OT es un SaaS multitenant para la gestión de órdenes de trabajo. Su
arquitectura funcional está documentada en `docs/` y no es sustituida por el
circuito agéntico.

**Baseline actual:** `v0.1.0` pre-release, con los Puntos 01–10 completados,
PostgreSQL y SQLite validados, y Template v2.0.0 operativo.

## Gobernanza v2

Las nuevas features usan `ASSESS → Planner → Builder → validaciones → Reviewer
→ convergence → HITL`. La profundidad SDD es proporcional al riesgo:
`LIGHT`, `STANDARD` o `FULL`.

La unidad nativa crea una rama y un worktree aislados. El merge requiere PR,
CI verde y autorización humana. Los runs anteriores a esta adopción son
evidencia legacy y permanecen intactos.

## Desarrollo

- Producto backend: `apps/api/`.
- Producto frontend/PWA: `apps/web/`.
- Tests de producto: `apps/api/tests/`.
- Tests de gobernanza: `tests/`.
- Fuente canónica del circuito: `.agentic/`.

No ejecutar migraciones ni modificar contratos de producto para adoptar la
gobernanza.
