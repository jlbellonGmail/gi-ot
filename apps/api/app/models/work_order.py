import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import HistoryEventType

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.location import Location
    from app.models.person import Customer, Technician
    from app.models.priority import Priority
    from app.models.sync_operation import SyncOperation
    from app.models.work_order_status import WorkOrderStatus
    from app.models.work_order_type import WorkOrderType

__all__ = ["HistoryEventType", "WorkOrder", "WorkOrderHistory", "WorkOrderPhoto"]


class WorkOrder(Base):
    """Orden de Trabajo, entidad central del producto (§4.12 modelo-datos.md).

    Toda referencia (customer, location, asset, technician, type, priority,
    status) pertenece al mismo tenant que la OT: la pertenencia se valida en
    la capa de negocio (services), no solo por FK (§4.12 restricciones).

    Estados con semántica interna fija (`code` de WorkOrderStatus):
    PENDING → IN_PROGRESS → COMPLETED | UNRESOLVED; reapertura controlada
    terminal → PENDING solo desde Oficina/Admin (modelo-funcional.md §9).
    """

    __tablename__ = "work_orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_work_orders_tenant_id"),
        UniqueConstraint("tenant_id", "number", name="uq_work_orders_tenant_number"),
        ForeignKeyConstraint(
            ["tenant_id", "customer_id"],
            ["customers.tenant_id", "customers.person_id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "technician_id"],
            ["technicians.tenant_id", "technicians.person_id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "location_id"],
            ["locations.tenant_id", "locations.id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "asset_id"],
            ["assets.tenant_id", "assets.id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "work_order_type_id"],
            ["work_order_types.tenant_id", "work_order_types.id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "priority_id"],
            ["priorities.tenant_id", "priorities.id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "status_id"],
            ["work_order_statuses.tenant_id", "work_order_statuses.id"],
        ),
        Index("ix_work_orders_tenant_status", "tenant_id", "status_id"),
        Index("ix_work_orders_tenant_technician", "tenant_id", "technician_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)

    customer_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("locations.id"), nullable=False, index=True
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assets.id"), nullable=False, index=True
    )
    technician_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)

    work_order_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("work_order_types.id"), nullable=False
    )
    priority_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("priorities.id"), nullable=False
    )
    status_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("work_order_statuses.id"), nullable=False
    )

    requested_description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    status: Mapped["WorkOrderStatus"] = relationship(foreign_keys=[status_id])
    work_order_type: Mapped["WorkOrderType"] = relationship(
        foreign_keys=[work_order_type_id]
    )
    priority: Mapped["Priority"] = relationship(foreign_keys=[priority_id])
    customer: Mapped["Customer"] = relationship(
        foreign_keys=[customer_id, tenant_id],
        primaryjoin="and_(WorkOrder.customer_id==Customer.person_id, WorkOrder.tenant_id==Customer.tenant_id)",
        viewonly=True,
    )
    technician: Mapped["Technician"] = relationship(
        foreign_keys=[technician_id, tenant_id],
        primaryjoin="and_(WorkOrder.technician_id==Technician.person_id, WorkOrder.tenant_id==Technician.tenant_id)",
        viewonly=True,
    )
    location: Mapped["Location"] = relationship(foreign_keys=[location_id])
    asset: Mapped["Asset"] = relationship(foreign_keys=[asset_id])
    history: Mapped[list["WorkOrderHistory"]] = relationship(
        back_populates="work_order",
        cascade="all, delete-orphan",
        foreign_keys="WorkOrderHistory.work_order_id",
    )
    photos: Mapped[list["WorkOrderPhoto"]] = relationship(
        back_populates="work_order",
        cascade="all, delete-orphan",
        foreign_keys="WorkOrderPhoto.work_order_id",
    )
    sync_operations: Mapped[list["SyncOperation"]] = relationship(
        back_populates="work_order",
        cascade="all, delete-orphan",
        foreign_keys="SyncOperation.entity_id",
    )


class WorkOrderHistory(Base):
    """Registro de auditoría de eventos relevantes de una OT: creación,
    asignación/reasignación de técnico, cambios de estado, reapertura.

    Fuente de verdad de trazabilidad: no se sobreescribe ni se borra
    (§4.17 modelo-datos.md).
    """

    __tablename__ = "work_order_history"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "work_order_id"],
            ["work_orders.tenant_id", "work_orders.id"],
            ondelete="CASCADE",
        ),
        Index("ix_work_order_history_tenant_wo", "tenant_id", "work_order_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[HistoryEventType] = mapped_column(
        SQLEnum(HistoryEventType, native_enum=False), nullable=False
    )
    previous_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    performed_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    work_order: Mapped[WorkOrder] = relationship(
        back_populates="history", foreign_keys=[work_order_id]
    )


class WorkOrderPhoto(Base):
    """Fotografía adjunta a una OT (§4.16 modelo-datos.md, ROADMAP §06).

    La base solo guarda metadatos y `storage_key` (ruta relativa dentro de
    `settings.uploads_dir`); el binario nunca se almacena en la base de
    datos (arquitectura.md §7, decisiones-producto.md §15).
    """

    __tablename__ = "work_order_photos"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "work_order_id"],
            ["work_orders.tenant_id", "work_orders.id"],
            ondelete="CASCADE",
        ),
        Index("ix_work_order_photos_tenant_wo", "tenant_id", "work_order_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str | None] = mapped_column(String(255), nullable=True)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    work_order: Mapped[WorkOrder] = relationship(
        back_populates="photos", foreign_keys=[work_order_id]
    )
