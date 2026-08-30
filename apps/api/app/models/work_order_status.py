import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorkOrderStatus(Base):
    """Estado de una OT, catálogo parametrizable por tenant (PRD §29).

    A diferencia de los demás catálogos, `code` es semántica interna FIJA
    (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `UNRESOLVED`) de la que depende
    el comportamiento del núcleo (modelo-datos.md §4.11): el tenant no crea
    ni elimina estados, solo puede renombrar `label` o desactivarlos.
    """

    __tablename__ = "work_order_statuses"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_work_order_statuses_tenant_code"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    is_terminal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)