"""Endpoints FastAPI para Comprobantes y Comunicaciones (ROADMAP §09).

Endpoints disponibles (prefix: /api/v1/receipts):
- POST /                              - Generar comprobante de OT
- GET  /{work_order_id}               - Obtener comprobante (HTML)
- GET  /{work_order_id}/pdf           - Descargar PDF
- POST /{work_order_id}/send-email    - Enviar por email
- POST /{work_order_id}/send-whatsapp - Enviar por WhatsApp
- GET  /branding                      - Obtener branding del tenant
- PUT  /branding                      - Actualizar branding del tenant
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_tenant_id, get_current_user, get_db
from app.core.config import get_settings
from app.models.user import User
from app.schemas.work_order_receipt import (
    TenantBranding,
    TenantBrandingUpdate,
    WhatsAppSend,
    WorkOrderReceiptGenerate,
    WorkOrderReceiptOut,
    WorkOrderReceiptSend,
)
from app.services.receipt import ReceiptService


router = APIRouter(prefix="/receipts", tags=["receipts"])


def _service(db: Session = Depends(get_db)) -> ReceiptService:
    return ReceiptService(db)


@router.post("", response_model=WorkOrderReceiptOut, status_code=status.HTTP_201_CREATED)
def generate_receipt(
    payload: WorkOrderReceiptGenerate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
) -> WorkOrderReceiptOut:
    """Genera el comprobante de una OT finalizada (HTML + PDF opcional)."""
    service = _service(db)
    try:
        receipt = service.generate_receipt(tenant_id, payload, generated_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return WorkOrderReceiptOut.model_validate(receipt)


@router.get("/{work_order_id}", response_class=HTMLResponse)
def get_receipt_html(
    work_order_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> HTMLResponse:
    """Devuelve el comprobable en HTML para visualizacion en navegador."""
    receipt = db.query(WorkOrderReceipt).filter_by(
        work_order_id=work_order_id, tenant_id=tenant_id
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    return HTMLResponse(content=receipt.content_html)


@router.get("/{work_order_id}/pdf")
def get_receipt_pdf(
    work_order_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> FileResponse:
    """Descarga el comprobable en PDF."""
    receipt = db.query(WorkOrderReceipt).filter_by(
        work_order_id=work_order_id, tenant_id=tenant_id
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    if not receipt.pdf_storage_key:
        raise HTTPException(status_code=404, detail="PDF no disponible")

    settings = get_settings()
    filepath = Path(settings.uploads_dir) / receipt.pdf_storage_key
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"comprobante_ot_{work_order_id}.pdf",
    )


@router.post("/{work_order_id}/send-email", status_code=status.HTTP_204_NO_CONTENT)
def send_receipt_email(
    work_order_id: uuid.UUID,
    payload: WorkOrderReceiptSend,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
) -> None:
    """Envia el comprobable por email al destinatario indicado."""
    service = _service(db)
    try:
        service.send_receipt_email(tenant_id, payload, sent_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{work_order_id}/send-whatsapp", status_code=status.HTTP_204_NO_CONTENT)
def send_receipt_whatsapp(
    work_order_id: uuid.UUID,
    payload: WhatsAppSend,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> None:
    """Envia el comprobable por WhatsApp (evaluacion tecnica/comercial, no bloquea MVP)."""
    service = _service(db)
    try:
        service.send_receipt_whatsapp(tenant_id, work_order_id, payload.phone)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/branding", response_model=TenantBranding)
def get_branding(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> TenantBranding:
    """Obtiene el branding del tenant para comprobantes (PRD §54)."""
    service = _service(db)
    return service._get_branding(tenant_id)


@router.put("/branding", response_model=TenantBranding)
def update_branding(
    payload: TenantBrandingUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
) -> TenantBranding:
    """Actualiza el branding del tenant (logo, colores, datos de contacto)."""
    service = _service(db)
    branding = service._get_branding(tenant_id)
    update_data = payload.model_dump(exclude_unset=True)
    updated = TenantBranding(
        company_name=update_data.get("company_name", branding.company_name),
        logo_url=update_data.get("logo_url", branding.logo_url),
        primary_color=update_data.get("primary_color", branding.primary_color),
        secondary_color=update_data.get("secondary_color", branding.secondary_color),
        address=update_data.get("address", branding.address),
        phone=update_data.get("phone", branding.phone),
        email=update_data.get("email", branding.email),
        website=update_data.get("website", branding.website),
        tax_id=update_data.get("tax_id", branding.tax_id),
    )
    service.update_branding(tenant_id, updated)
    return updated