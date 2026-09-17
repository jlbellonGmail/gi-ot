# HISTORICAL MIGRATION REPAIR

`sync_operations` fue introducida en Punto 08 mediante modelo, servicios,
endpoint y `create_all()`, pero no mediante Alembic. `7f` asumía que la tabla
y un índice previo ya existían.

Alcance aplicado:

- `7f`: crea el esquema histórico demostrable y elimina el DROP inválido.
- `9c`: conserva branding, materializa `sort_order` omitido y deja de operar sobre `work_order_id`.
- `a10f2c3d4e5f`: bridge forward idempotente y no destructivo.

No se cambió el orden anterior ni se modificó PR #2. Replay SQLite vacío,
HEAD único, downgrade/re-upgrade y `alembic check`: PASS. PostgreSQL real queda
pendiente de GitHub Actions.
