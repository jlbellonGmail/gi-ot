# SDD — 10-validacion-postgresql

## Contexto

Punto 10 comenzó antes de Template v2. PR #2 se conserva como referencia
legacy y no se mergea, rebasea ni modifica.

## Objetivo funcional

GI-OT debe operar y validarse correctamente sobre PostgreSQL manteniendo
SQLite, multitenancy, RBAC, autenticación, offline/sync, comprobantes y los
contratos `/api/v1`.

## Incluye

- PostgreSQL reproducible y configuración por entorno.
- psycopg y Alembic.
- RLS, tenant isolation, constraints y FKs.
- Fixtures válidos para SQLite y PostgreSQL.
- Suite PostgreSQL y compatibilidad SQLite.
- Gate PostgreSQL separado dentro del CI v2.
- Correcciones estrictamente necesarias para esta validación.

## No incluye

- Nuevas funcionalidades o APIs.
- Cambio de ORM, framework o arquitectura SaaS.
- Microservicios, eventos, brokers, GraphQL, CQRS o Kubernetes.
- Mejoras oportunistas no necesarias para Punto 10.

## Restricciones

- No modificar PR #2 ni su rama.
- No modificar migraciones históricas existentes salvo bloqueo demostrado.
- No deshabilitar RLS, constraints ni validaciones para obtener verde.
- No crear tags ni releases.

## Criterios de aceptación

- PostgreSQL reproducible y conexión válida.
- Alembic desde base vacía, HEAD único y downgrade/re-upgrade válidos.
- RLS bloquea accesos cross-tenant directos.
- Auth, tenant context, RBAC y PLATFORM_OWNER funcionan.
- Suite PostgreSQL completa verde.
- Suite SQLite completa verde.
- Cero errores nuevos de mypy, Ruff, ESLint y TypeScript.
- Backend y frontend build verdes.
- CI governance/product/PostgreSQL separado.
- Evidencia v2 completa, Reviewer aprobado y HITL pendiente de merge.
