"""Modelo WorkOrderReceipt — Comprobante de OT (ROADMAP §09).

Un comprobante se genera al finalizar una OT y contiene:
- Datos de la empresa (branding)
- Datos de la OT (número, fechas, descripción, técnico)
- Datos del cliente
- Firma digital opcional
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WorkOrderReceipt(Base):
    __tablename__ = "work_order_receipts"

    __table_args__ = (
        Index("ix_wor_receipt_tenant_wo", "tenant_id", "work_order_id"),
        ForeignKeyConstraint(
            ["tenant_id", "work_order_id"],
            ["work_orders.tenant_id", "work_orders.id"],
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_order_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    generated_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    sent_to_email: Mapped[bool] = mapped_column(default=False, nullable=False)
    sent_to_whatsapp: Mapped[bool] = mapped_column(default=False, nullable=False)
    last_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    work_order: Mapped["WorkOrder"] = relationship()
