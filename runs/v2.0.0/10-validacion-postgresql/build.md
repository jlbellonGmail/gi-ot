# Build — Punto 10

- `7f` materializa `sync_operations` respaldada por Git.
- `9c` conserva branding, materializa `sort_order` y elimina la referencia inválida a `work_order_id`.
- `a10f2c3d4e5f` normaliza estados existentes sin borrar datos.
- `b17f2a6c9d10` mantiene el único head y aplica RLS/constraints de Punto 10.
- `psycopg` queda en runtime; calidad queda en `requirements-dev.txt`.
