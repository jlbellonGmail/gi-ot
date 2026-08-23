import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Única plantilla existente en el MVP. El modelo admite agregar plantillas
# por rubro en el futuro (p. ej. CLIMATIZACION, ASCENSORES, ALARMAS) sin
# cambios estructurales — basta con insertar una nueva fila `ConfigTemplate`
# y sus filas `Template*` asociadas.
DEFAULT_TEMPLATE_CODE = "DEFAULT"


class ConfigTemplate(Base):
    """Plantilla de configuración inicial del sistema.

    No pertenece a ningún tenant: es un catálogo de plataforma, análogo a
    `Role`. Contiene el conjunto de valores estándar (estados de OT,
    prioridades, tipos de trabajo, tipos de activo) que se copian a la
    configuración propia de un tenant al crearlo (`app.core.provisioning`).
    `code` identifica la plantilla de forma estable; `name` es la etiqueta
    visible en herramientas de administración de plataforma.
    """

    __tablename__ = "config_templates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
