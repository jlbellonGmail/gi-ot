# QA — 10-validacion-postgresql

## Estado

PASS.

## Cobertura ejecutada

- SQLite funcional completa: PASS.
- PostgreSQL funcional y RLS: PASS (`5 passed`).
- PostgreSQL vacío → HEAD y reversibilidad HEAD → `9c8b2c1d4e5f` → HEAD: PASS.
- Storage local tenant-scoped y fotos: PASS.
- Inspección SQL: rol `NOSUPERUSER NOBYPASSRLS`; tablas tenant con RLS/FORCE y policies `USING`/`WITH CHECK`: PASS.

## Riesgos conocidos

La deuda histórica de Ruff/ESLint queda cubierta por baseline; los ratchets reportaron cero regresiones nuevas.
