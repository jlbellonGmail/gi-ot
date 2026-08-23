import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Priority(Base):
    """Prioridad de una OT, catálogo parametrizable por tenant (PRD §30).

    Se provisiona copiando `TemplatePriority` de la plantilla de
    configuración del tenant al crearlo (`app.core.provisioning`); el
    tenant puede ampliar el conjunto o renombrar las etiquetas.
    `sort_order` determina el orden de presentación.
    """

    __tablename__ = "priorities"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_priorities_tenant_code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
