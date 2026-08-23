from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa común a todos los modelos.

    Importar aquí (no en session.py) evita ciclos: Alembic importa
    `app.db.base` para descubrir metadata sin necesitar un engine activo.
    """
