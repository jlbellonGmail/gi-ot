# gi-ot API

FastAPI + SQLAlchemy + Alembic. Ver `docs/tecnica/arquitectura.md` y `docs/tecnica/stack.md` en la raíz del proyecto para el diseño completo.

## Desarrollo local

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows
# .venv/bin/pip install -r requirements.txt     # Linux/Mac

cp .env.example .env

python -m alembic upgrade head

# Primer usuario PLATFORM_OWNER (una sola vez por entorno):
python scripts/create_platform_owner.py owner@tuempresa.com "TuPassword123!" "Nombre Apellido"

python -m uvicorn app.main:app --reload
```

API disponible en `http://127.0.0.1:8000`, documentación interactiva en `/docs`.

## Tests

```bash
python -m pytest
```

Los tests usan una base SQLite en memoria, aislada de `data/gi-ot.db` (desarrollo local).

## Persistencia

BOOTSTRAP usa SQLite (`DATABASE_URL` en `.env`). El mismo modelo y las mismas migraciones Alembic aplican sobre PostgreSQL en producción, cambiando únicamente `DATABASE_URL` (docs/tecnica/arquitectura.md §6).
