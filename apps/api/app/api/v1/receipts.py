"""Endpoints FastAPI para Comprobantes y Comunicaciones (ROADMAP §09).

Endpoints disponibles (prefix: /api/v1/receipts):
- POST /                    - Generar comprobante de OT
- GET  /{work_order_id}     - Obtener comprobante (HTML)
- GET  /{work_order_id}/pdf - Descargar PDF
- POST /{work_order_id}/send-email - Enviar por email
"""

import uuid
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_tenant_id, get_current_user, get_db
from app.core.config import get_settings
from app.models.user import User
from app.models.work_order import WorkOrder
from app.models.work_order_receipt import WorkOrderReceipt
from app.schemas.work_order_receipt import WorkOrderReceiptGenerate, WorkOrderReceiptOut, WorkOrderReceiptSend
from app.services.receipt import ReceiptService


router = APIRouter(prefix="/receipts", tags=["receipts"])


def _service(db: Session = Depends(get_db)) -> ReceiptService:
    return ReceiptService(db)


@router.post("", response_model=WorkOrderReceiptOut, status_code=201)
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
    """Devuelve el comprobante en HTML para visualizacion en navegador."""
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
    """Descarga el comprobante en PDF."""
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


@router.post("/{work_order_id}/send-email", status_code=204)
def send_receipt_email(
    work_order_id: uuid.UUID,
    payload: WorkOrderReceiptSend,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
) -> None:
    """Envia el comprobante por email al destinatario indicado."""
    service = _service(db)
    try:
        service.send_receipt_email(tenant_id, payload, sent_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))