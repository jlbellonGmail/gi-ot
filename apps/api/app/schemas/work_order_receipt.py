"""Schemas Pydantic para WorkOrderReceipt — Comprobantes (ROADMAP §09)."""

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
    pdf_storage_key: Optional[str] = None
    generated_by: uuid.UUID
    generated_at: datetime
    sent_to_email: bool
    sent_to_whatsapp: bool
    last_sent_at: Optional[datetime] = None


class WorkOrderReceiptGenerate(BaseModel):
    """Request para generar un comprobante."""
    work_order_id: uuid.UUID
    # Opcional: forzar regeneración si ya existe
    force_regenerate: bool = False


class WorkOrderReceiptSend(BaseModel):
    """Request para enviar un comprobante por email."""
    work_order_id: uuid.UUID
    recipient_email: str
    subject: Optional[str] = None
    body: Optional[str] = None


class TenantBranding(BaseModel):
    """Configuración de branding del tenant para comprobantes."""
    company_name: str
    logo_url: Optional[str] = None
    primary_color: str = "#0f172a"
    secondary_color: str = "#1e293b"
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None  # CUIT/NIF