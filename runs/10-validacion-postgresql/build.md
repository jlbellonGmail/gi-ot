# Build — 10-validacion-postgresql

## Estado

PASS técnico.

## Evidencia

- PostgreSQL 17 vacío: `alembic upgrade head` PASS.
- `alembic check`: PASS, sin operaciones nuevas.
- Suite SQLite: PASS.
- Suite PostgreSQL/RLS: `5 passed`.
- Storage/fotos: PASS.
- Quality ratchet Ruff, Mypy, ESLint y TypeScript: PASS sin regresiones nuevas.
- Frontend lint, typecheck y Next build: PASS.
- `git diff --check`: PASS.

## Cambios funcionales

- Relaciones SQLAlchemy desambiguadas para FKs compuestas.
- JOIN persona-identificación con tenant explícito.
- `SyncOperation` alineado con `DateTime(timezone=True)`.
- Fixture RLS usa `example.com`; el dominio `.test` era rechazado por email-validator.

No se modificaron migraciones históricas previas; la migración `a10f4c2d9e01` es la revisión nueva de Punto 10.
