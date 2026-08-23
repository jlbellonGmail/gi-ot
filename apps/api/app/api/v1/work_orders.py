"""Endpoints FastAPI para el módulo WorkOrder (Etapa 04 — ROADMAP.md §04).

Rutas disponibles (prefix: /api/v1/work-orders):
- GET          /                 — Listar OT con filtros opcionales
- POST         /                 — Crear nueva OT (Oficina/Admin)
- GET          /{wo_id}          — Obtener OT por ID
- PATCH        /{wo_id}          — Actualizar campos no ejecutivos (solo si no es terminal)
- POST         /{wo_id}/assign        — Asignar técnico (Oficina/Admin)
- POST         /{wo_id}/start         — Iniciar OT
- POST         /{wo_id}/register-work — Registrar trabajo realizado (mientras está en curso)
- POST         /{wo_id}/finish        — Finalizar OT (COMPLETED/UNRESOLVED)
- POST         /{wo_id}/reopen        — Reapertura controlada (Oficina/Admin)
- GET          /{wo_id}/history       — Historial de auditoría
- POST         /{wo_id}/photos            — Subir fotografía
- GET          /{wo_id}/photos            — Listar fotografías
- GET          /{wo_id}/photos/{photo_id}/file — Servir el binario de una fotografía
- DELETE       /{wo_id}/photos/{photo_id}     — Eliminar fotografía
"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_tenant_id, get_current_user, require_roles
from app.db.session import get_db
from app.exceptions import (
    InvalidTransition,
    RefValidationError,
    TechnicianNotFound,
    TechnicianNotLinked,
    TerminalWorkOrder,
    WorkOrderNotFound,
)
from app.models.role import TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN
from app.models.user import User
from app.models.work_order import WorkOrder
from app.schemas.work_order import (
    WorkOrderAssign,
    WorkOrderCreate,
    WorkOrderFinish,
    WorkOrderHistoryOut,
    WorkOrderOut,
    WorkOrderPhotoOut,
    WorkOrderRegisterWork,
    WorkOrderReopen,
    WorkOrderUpdate,
)
from app.services.work_order import WorkOrderService

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

_manage_roles = require_roles(TENANT_ADMIN, TENANT_OFFICE)
_create_roles = require_roles(TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN)


def _service(db: Session = Depends(get_db)) -> WorkOrderService:
    return WorkOrderService(db)


def _to_out(wo: WorkOrder) -> WorkOrderOut:
    return WorkOrderOut(
        id=wo.id,
        tenant_id=wo.tenant_id,
        number=wo.number,
        customer_id=wo.customer_id,
        location_id=wo.location_id,
        asset_id=wo.asset_id,
        technician_id=wo.technician_id,
        work_order_type_id=wo.work_order_type_id,
        priority_id=wo.priority_id,
        status_id=wo.status_id,
        requested_description=wo.requested_description,
        performed_description=wo.performed_description,
        scheduled_at=wo.scheduled_at,
        started_at=wo.started_at,
        finished_at=wo.finished_at,
        created_by=wo.created_by,
        updated_by=wo.updated_by,
        created_at=wo.created_at,
        updated_at=wo.updated_at,
        status_code=wo.status.code if wo.status else None,
        status_label=wo.status.label if wo.status else None,
        is_terminal=wo.status.is_terminal if wo.status else False,
        priority_code=wo.priority.code if wo.priority else None,
        priority_label=wo.priority.label if wo.priority else None,
    )


_DOMAIN_ERROR_STATUS = {
    WorkOrderNotFound: status.HTTP_404_NOT_FOUND,
    TechnicianNotFound: status.HTTP_404_NOT_FOUND,
    TechnicianNotLinked: status.HTTP_403_FORBIDDEN,
    RefValidationError: status.HTTP_400_BAD_REQUEST,
    InvalidTransition: status.HTTP_409_CONFLICT,
    TerminalWorkOrder: status.HTTP_409_CONFLICT,
}


def _raise_from(e: Exception) -> None:
    for exc_type, http_status in _DOMAIN_ERROR_STATUS.items():
        if isinstance(e, exc_type):
            raise HTTPException(status_code=http_status, detail=str(e)) from e
    raise  # pragma: no cover


# ── LISTAR ──────────────────────────────────────────────────────────

@router.get("", response_model=List[WorkOrderOut])
def list_wo(
    status_code: Optional[str] = Query(default=None, description="Código de estado (PENDING/IN_PROGRESS/COMPLETED/UNRESOLVED)"),
    technician_id: Optional[uuid.UUID] = Query(default=None),
    customer_id: Optional[uuid.UUID] = Query(default=None),
    priority_id: Optional[uuid.UUID] = Query(default=None),
    location_id: Optional[uuid.UUID] = Query(default=None),
    asset_id: Optional[uuid.UUID] = Query(default=None),
    q: Optional[str] = Query(default=None, description="Búsqueda libre: número, cliente, ubicación, activo o descripción"),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    sort: Optional[str] = Query(default=None, description="date_desc (default) | date_asc | priority | updated | status"),
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> List[WorkOrderOut]:
    """Lista operativa de OT del tenant: búsqueda + filtros + orden se
    combinan libremente (ROADMAP §07, UI-UX-STANDARDS.md §10). Cualquier
    rol autenticado."""
    service = _service(db)
    wo_list = service.list_wo(
        tenant_id,
        status_code=status_code,
        technician_id=technician_id,
        customer_id=customer_id,
        priority_id=priority_id,
        location_id=location_id,
        asset_id=asset_id,
        q=q,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
    )
    return [_to_out(wo) for wo in wo_list]


# ── CREAR ──────────────────────────────────────────────────────────

@router.post("", response_model=WorkOrderOut, status_code=status.HTTP_201_CREATED)
def create_wo(
    payload: WorkOrderCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_create_roles),
) -> WorkOrderOut:
    """Crear nueva OT. Oficina/Admin crea con los datos enviados; un
    Técnico crea una OT urgente desde el campo (PRD §20) — el backend
    fuerza prioridad URGENT y se autoasigna, ignorando lo recibido en
    `priority_id`/`technician_id`."""
    service = _service(db)
    try:
        if current_user.role.code == TENANT_TECHNICIAN:
            wo = service.create_wo_as_technician(
                tenant_id, payload, technician_user_id=current_user.id, created_by=current_user.id
            )
        else:
            wo = service.create_wo(tenant_id, payload, created_by=current_user.id)
    except (RefValidationError, TechnicianNotFound, TechnicianNotLinked) as e:
        _raise_from(e)
    return _to_out(wo)


# ── OBTENER UNO ───────────────────────────────────────────────────

@router.get("/{wo_id}", response_model=WorkOrderOut)
def get_wo(
    wo_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> WorkOrderOut:
    """Obtener OT por ID. Cualquier rol autenticado del tenant."""
    service = _service(db)
    try:
        wo = service.get_wo(tenant_id, wo_id)
    except WorkOrderNotFound as e:
        _raise_from(e)
    return _to_out(wo)


# ── ACTUALIZAR (no ejecutivos) ────────────────────────────────────

@router.patch("/{wo_id}", response_model=WorkOrderOut)
def update_wo(
    wo_id: uuid.UUID,
    payload: WorkOrderUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_manage_roles),
) -> WorkOrderOut:
    """Actualizar descripción solicitada, scheduled_at, type o priority.
    Solo mientras la OT no haya alcanzado estado terminal."""
    service = _service(db)
    try:
        wo = service.update_wo(tenant_id, wo_id, payload)
    except (WorkOrderNotFound, TerminalWorkOrder, RefValidationError) as e:
        _raise_from(e)
    return _to_out(wo)


# ── ASIGNAR TÉCNICO ───────────────────────────────────────────────

@router.post("/{wo_id}/assign", response_model=WorkOrderOut)
def assign_technician(
    wo_id: uuid.UUID,
    payload: WorkOrderAssign,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> WorkOrderOut:
    """Asignar técnico a OT. Oficina/Admin."""
    service = _service(db)
    try:
        wo = service.assign_technician(tenant_id, wo_id, payload.technician_id, performed_by=current_user.id)
    except (WorkOrderNotFound, TechnicianNotFound, TerminalWorkOrder) as e:
        _raise_from(e)
    return _to_out(wo)


# ── INICIAR OT ────────────────────────────────────────────────────

@router.post("/{wo_id}/start", response_model=WorkOrderOut)
def start_wo(
    wo_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
) -> WorkOrderOut:
    """Iniciar OT: PENDING → IN_PROGRESS. Cualquier usuario del tenant
    (Oficina, Admin o Técnico, este último desde flujo de campo)."""
    service = _service(db)
    try:
        wo = service.start_wo(tenant_id, wo_id, performed_by=current_user.id)
    except (InvalidTransition, WorkOrderNotFound) as e:
        _raise_from(e)
    return _to_out(wo)


# ── REGISTRAR TRABAJO REALIZADO ────────────────────────────────────

@router.post("/{wo_id}/register-work", response_model=WorkOrderOut)
def register_work(
    wo_id: uuid.UUID,
    payload: WorkOrderRegisterWork,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
) -> WorkOrderOut:
    """Registrar el trabajo realizado mientras la OT está en curso.
    Cualquier usuario del tenant (típicamente el técnico en campo)."""
    service = _service(db)
    try:
        wo = service.register_work(tenant_id, wo_id, payload.performed_description, performed_by=current_user.id)
    except (WorkOrderNotFound, TerminalWorkOrder) as e:
        _raise_from(e)
    return _to_out(wo)


# ── FINALIZAR OT ────────────────────────────────────────────────────

@router.post("/{wo_id}/finish", response_model=WorkOrderOut)
def finish_wo(
    wo_id: uuid.UUID,
    payload: WorkOrderFinish,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
) -> WorkOrderOut:
    """Finalizar OT: IN_PROGRESS → COMPLETED o UNRESOLVED. Cualquier usuario
    del tenant puede finalizar (el técnico desde campo, oficina desde admin)."""
    service = _service(db)
    try:
        wo = service.finish_wo(tenant_id, wo_id, payload, performed_by=current_user.id)
    except (InvalidTransition, WorkOrderNotFound) as e:
        _raise_from(e)
    return _to_out(wo)


# ── REAPERTURA ────────────────────────────────────────────────────

@router.post("/{wo_id}/reopen", response_model=WorkOrderOut)
def reopen_wo(
    wo_id: uuid.UUID,
    payload: WorkOrderReopen,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> WorkOrderOut:
    """Reapertura controlada: solo Oficina/Admin. Estados terminales → PENDING,
    requiere `notes` obligatorio para preservar trazabilidad."""
    service = _service(db)
    try:
        wo = service.reopen_wo(tenant_id, wo_id, payload, performed_by=current_user.id)
    except (InvalidTransition, WorkOrderNotFound) as e:
        _raise_from(e)
    return _to_out(wo)


# ── HISTORIAL ─────────────────────────────────────────────────────

@router.get("/{wo_id}/history", response_model=List[WorkOrderHistoryOut])
def history_wo(
    wo_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> List[WorkOrderHistoryOut]:
    """Historial de auditoría de una OT. Cualquier rol autenticado del tenant."""
    service = _service(db)
    try:
        history_rows = service.get_history(tenant_id, wo_id)
    except WorkOrderNotFound as e:
        _raise_from(e)
    return [WorkOrderHistoryOut.model_validate(h) for h in history_rows]


# ── FOTOGRAFÍAS ───────────────────────────────────────────────────

@router.post("/{wo_id}/photos", response_model=WorkOrderPhotoOut, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    wo_id: uuid.UUID,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
) -> WorkOrderPhotoOut:
    """Sube una fotografía de la OT (típicamente el técnico en campo).
    El original nunca se sobreescribe (decisiones-producto.md §15)."""
    service = _service(db)
    file_bytes = await file.read()
    try:
        photo = service.add_photo(
            tenant_id,
            wo_id,
            file_bytes=file_bytes,
            content_type=file.content_type,
            caption=caption,
            uploaded_by=current_user.id,
        )
    except (WorkOrderNotFound, TerminalWorkOrder, RefValidationError) as e:
        _raise_from(e)
    return WorkOrderPhotoOut.model_validate(photo)


@router.get("/{wo_id}/photos", response_model=List[WorkOrderPhotoOut])
def list_photos(
    wo_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> List[WorkOrderPhotoOut]:
    """Lista las fotografías de una OT. Cualquier rol autenticado del tenant."""
    service = _service(db)
    try:
        photos = service.list_photos(tenant_id, wo_id)
    except WorkOrderNotFound as e:
        _raise_from(e)
    return [WorkOrderPhotoOut.model_validate(p) for p in photos]


@router.get("/{wo_id}/photos/{photo_id}/file")
def get_photo_file(
    wo_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> FileResponse:
    """Sirve el binario de una fotografía. Siempre pasa por la API, que
    valida pertenencia al tenant antes de servir el archivo (arquitectura.md §7)."""
    service = _service(db)
    try:
        path = service.get_photo_file_path(tenant_id, wo_id, photo_id)
    except WorkOrderNotFound as e:
        _raise_from(e)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")
    return FileResponse(path)


@router.delete("/{wo_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    wo_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(get_current_user),
) -> None:
    """Elimina una fotografía de la OT (solo mientras no sea terminal)."""
    service = _service(db)
    try:
        service.delete_photo(tenant_id, wo_id, photo_id)
    except (WorkOrderNotFound, TerminalWorkOrder) as e:
        _raise_from(e)
