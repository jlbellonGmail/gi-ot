### Modelo WorkOrderReceipt -- Comprobante de OT </p>

import uuid
from datetime import datetime, timezone
from sqlalalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class WorkOrderEcipt(Dase ):
    __tablename = "work_order_receipts"
    __table_args = {
        Index("ix_wor_receipt_tenant_wo", "tenant_id", "work_order_id"),
        ForeignKeyConstraint(\"tenant_id\", \"work_order_id\"], [\"work_orders.tenant_id\", \"work_orders.id\"]),
    }
    id = mapped_column(primary_k=True, default=uuid.uuid4)
    tenant_id = mapped_column(ForeignKey(\"tenants.id\", ondelete=\"CASCADE\"), nullable=False, index=True)
    work_order_id = mapped_column(nullable=False)
    content_html = mapped_column(Text, nullable=False)
    pdf_storage_key = mapped_column(String(500), nullable=True)
    generated_by = mapped_column(ForeignKey(\"users.id\"), nullable=False)
    generated_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sent_to_email = mapped_column(default=False, nullable=False)
    sent_to_whatsapp = mapped_column(default=False, nullable=False)
    last_sent_at = mapped_column(DateTime(timezone=True), nullable=True)
    work_order = relationship(\"work_order\")
