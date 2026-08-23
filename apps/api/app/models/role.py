from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Códigos estables — ver docs/producto/decisiones-producto.md §4.
PLATFORM_OWNER = "PLATFORM_OWNER"
TENANT_ADMIN = "TENANT_ADMIN"
TENANT_OFFICE = "TENANT_OFFICE"
TENANT_TECHNICIAN = "TENANT_TECHNICIAN"

ALL_ROLE_CODES = (PLATFORM_OWNER, TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN)


class Role(Base):
    """Catálogo fijo de plataforma (no parametrizable por tenant).

    `code` es la semántica interna estable de la que depende la lógica de
    negocio; `default_label` es la etiqueta visible por defecto, que un
    tenant podrá sobreescribir en la UI sin tocar `code` (modelo-datos.md §4.4).
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    default_label: Mapped[str] = mapped_column(String(100), nullable=False)
