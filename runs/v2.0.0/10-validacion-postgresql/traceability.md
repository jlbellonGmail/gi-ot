# Trazabilidad legacy → v2

| Archivo/cambio legacy | Commit origen | Decisión | Destino v2 | Motivo |
|---|---|---|---|---|
| PR #2 completa | `887ed4e`..`03a6f3b` | REUTILIZAR SELECTIVAMENTE | Esta work unit | No se copia ni se cherry-pickea completa |
| Evidencia `runs/10-validacion-postgresql/**` | varios | REGENERAR | Evidencia v2 | Es trabajo iniciado antes de Template v2 |
| `.github/workflows/ci.yml` legacy | `e5e63ce` | ADAPTAR | CI v2 | No reemplazar governance CI |
| Migraciones históricas modificadas | varios | ADAPTAR | Revisión previa | No modificar históricas automáticamente |
| Migración `a10f4c2d9e01` | `1b28abd` | REUTILIZAR/ADAPTAR | Alembic v2 | Revisar contra HEAD actual |
| `app/db/rls.py` | `1b28abd` | REUTILIZAR | API/DB | Base técnica de contexto RLS |
| Tests `tests_postgresql` | `05862d3` | REUTILIZAR/ADAPTAR | Tests producto | RLS pasa; suite funcional requiere corrección |
| `compose.postgres.yml` | `1b28abd` | REUTILIZAR | Infra validación | Entorno reproducible |
| Storage tenant-scoped | `1b28abd` | ADAPTAR | Storage | Sólo si es requisito de Punto 10 |
| `sync_operations` ausente de Alembic | `b792741`, `7b3447a`, `430b35e` | ADAPTAR | `7f8a9b2c1d4e` | El modelo existía fuera de Alembic; se reconstruye desde evidencia Git |
| `7f` DROP INDEX obsoleto | `430b35e` | REEMPLAZAR | `7f8a9b2c1d4e` | No existe tabla ni índice en la cadena previa |
| Reparación parcial de `9c` | `7b3447a` | ADAPTAR | `9c8b2c1d4e5f` | Se elimina la referencia inválida a `work_order_id` |
| Estados legacy ya versionados sin sync | diagnóstico v2 | INCORPORAR | `a10f2c3d4e5f` | Bridge idempotente, preserva datos y falla ante columnas no inferibles |
| `sort_order` de estados omitido del replay | `7b3447a` | ADAPTAR | `9c8b2c1d4e5f` | El modelo ejecutable ya lo requería |
