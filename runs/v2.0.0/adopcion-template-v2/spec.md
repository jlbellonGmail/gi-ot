# SPEC: adopcion-template-v2

## Alcance

Incluye la gobernanza, lifecycle, roles canónicos, ASSESS, SDD adaptativo,
work units, evidencia, auditoría y gates necesarios para nuevas features.

Excluye producto, API `/api/v1`, autenticación, RBAC, multitenancy, SQLAlchemy,
Alembic, frontend, PWA, offline, sync, fotos, comprobantes, branding, SMTP y
la PR #2 de PostgreSQL.

## Contrato

- Planner, Builder y Reviewer son roles conceptuales independientes de proveedor.
- Analyst, QA y Code Reviewer se conservan como aliases/capacidades legacy.
- ASSESS selecciona LIGHT, STANDARD o FULL de forma determinística.
- SUMMARY es la entrada humana; `runs/` es evidencia primaria.
- `.audit/` es independiente de Reviewer, CI y HITL.
- MCP comienza vacío.
- Merge y release requieren HITL.

## Compatibilidad

`runs/09-comprobantes/**` y `runs/activar-ai-native/**` son LEGACY EVIDENCE —
PRE TEMPLATE V2 y no se modifican ni reinterpretan.

## Aceptación

- [ ] Tests de gobernanza verdes.
- [ ] Tests de producto del baseline verdes.
- [ ] CI separado entre gobernanza y producto.
- [ ] Adaptadores sin drift.
- [ ] No hay cambios funcionales protegidos.
- [ ] HITL explícito antes del merge.
