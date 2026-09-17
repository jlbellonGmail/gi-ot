import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorkOrderType(Base):
    """Tipo de trabajo de una OT, catálogo parametrizable por tenant (PRD §31).

    Se provisiona copiando `TemplateWorkOrderType` de la plantilla de
    configuración del tenant al crearlo (`app.core.provisioning`), que el
    tenant puede ampliar o renombrar.
    """

    __tablename__ = "work_order_types"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_work_order_types_tenant_code"),
        UniqueConstraint("tenant_id", "id", name="uq_work_order_types_tenant_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
