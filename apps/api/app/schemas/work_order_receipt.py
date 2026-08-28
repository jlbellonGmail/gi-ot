"""Schemas Pydantic para WorkOrderReceipt -- Comprobantes (ROADMAP §09)."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class WorkOrderReceiptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    work_order_id: uuid.UUID
    content_html: str
    pdf_storage_key: str | None = None
    generated_by: uuid.UUID
    generated_at: datetime
    sent_to_email: bool
    sent_to_whatsapp: bool
    last_sent_at: datetime | None = None


class WorkOrderReceiptGenerate(BaseModel):
    """Request para generar un comprobante."""
    work_order_id: uuid.UUID
    force_regenerate: bool = False


class WorkOrderReceiptSend(BaseModel):
    """Request para enviar un comprobante por email."""
    work_order_id: uuid.UUID
    recipient_email: str
    subject: str | None = None
    body: str | None = None


class TenantBranding(BaseModel):
    """Configuracion de branding del tenant para comprobantes."""
    company_name: str
    logo_url: str | None = None
    primary_color: str = "#0f172a"
    secondary_color: str = "#1e293b"
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    tax_id: str | None = None
