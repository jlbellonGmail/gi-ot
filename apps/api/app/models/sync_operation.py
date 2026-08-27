"""Modelo SyncOperation — Rastrea operaciones pendientes de sincronización offline (ROADMAP §08).

Cada vez que el técnico realiza una escritura en campo sin conexión, se guarda
un registro aquí. Cuando vuelve la conectividad, el cliente envía estas
operaciones al endpoint /api/v1/sync y el backend las aplica idempotentemente.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import HistoryEventType


class SyncOperation(Base):
    __tablename__ = "sync_operations"

    __table_args__ = (
        Index("ix_sync_ops_tenant_status", "tenant_id", "status", "created_at"),
        Index("ix_sync_ops_tenant_wo", "tenant_id", "work_order_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Tipo de operación: "create_wo", "update_wo", "register_work", "finish_wo",
    # "add_photo", "reopen_wo", etc.
    operation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # ID de la entidad afectada (work_order_id u otro)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True
    )
    # Payload serializado con los datos de la operación
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    # Estado: "pending", "synced", "error"
    status: Mapped[str] = mapped_column(
        default="pending", nullable=False
    )
    # Intento actual (para reintentos)
    attempt: Mapped[int] = mapped_column(default=1, nullable=False)
    # Máximo de reintentos
    max_attempts: Mapped[int] = mapped_column(default=3, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    synced_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relación con la OT (opcional, depende del operation_type)
    work_order: Mapped["WorkOrder | None"] = relationship(
        back_populates="sync_operations", cascade="all, delete-orphan"
    )