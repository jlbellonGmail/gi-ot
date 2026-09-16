# Test report — 10-validacion-postgresql

PASS local:

- `apps/api/tests`: 106 passed.
- `apps/api/tests_migrations`: 3 passed.
- `alembic upgrade head` SQLite desde base vacía: PASS.
- `alembic heads`: un único head `b17f2a6c9d10`.
- downgrade a `9c8b2c1d4e5f` y upgrade a head: PASS.
- `alembic check` sobre replay SQLite: PASS.
- mypy ratchet: PASS, sin errores nuevos.
- Ruff ratchet: PASS, sin errores nuevos.
- compileall: PASS.
- Frontend `npm run build`: PASS.

PENDING REMOTE POSTGRESQL VALIDATION: Docker local no está disponible.
