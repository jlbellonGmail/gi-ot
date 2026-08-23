import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_tenant_id, require_roles
from app.db.session import get_db
from app.models.asset_type import AssetType
from app.models.priority import Priority
from app.models.role import TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN
from app.models.user import User
from app.models.work_order_status import WorkOrderStatus
from app.models.work_order_type import WorkOrderType
from app.schemas.catalog import (
    AssetTypeCreate,
    AssetTypeOut,
    AssetTypeUpdate,
    PriorityCreate,
    PriorityOut,
    PriorityUpdate,
    WorkOrderStatusOut,
    WorkOrderStatusUpdate,
    WorkOrderTypeCreate,
    WorkOrderTypeOut,
    WorkOrderTypeUpdate,
)

# Los tres roles del tenant pueden consultar los catálogos (el técnico los
# necesita para crear una OT urgente en campo, PRD §33). Solo el
# administrador de empresa puede modificarlos (PRD §18).
_read_roles = require_roles(TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN)
_manage_roles = require_roles(TENANT_ADMIN)

asset_types_router = APIRouter(prefix="/asset-types", tags=["asset-types"])
work_order_types_router = APIRouter(prefix="/work-order-types", tags=["work-order-types"])
priorities_router = APIRouter(prefix="/priorities", tags=["priorities"])
work_order_statuses_router = APIRouter(prefix="/work-order-statuses", tags=["work-order-statuses"])


@asset_types_router.get("", response_model=list[AssetTypeOut])
def list_asset_types(
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> list[AssetType]:
    return list(db.scalars(select(AssetType).where(AssetType.tenant_id == tenant_id).order_by(AssetType.label)))


@asset_types_router.post("", response_model=AssetTypeOut, status_code=status.HTTP_201_CREATED)
def create_asset_type(
    payload: AssetTypeCreate,
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_manage_roles),
) -> AssetType:
    asset_type = AssetType(tenant_id=tenant_id, code=payload.code, label=payload.label)
    db.add(asset_type)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un tipo de activo con ese código") from None
    db.refresh(asset_type)
    return asset_type


@asset_types_router.patch("/{asset_type_id}", response_model=AssetTypeOut)
def update_asset_type(
    asset_type_id: uuid.UUID,
    payload: AssetTypeUpdate,
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_manage_roles),
) -> AssetType:
    asset_type = db.scalar(
        select(AssetType).where(AssetType.id == asset_type_id, AssetType.tenant_id == tenant_id)
    )
    if asset_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de activo no encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset_type, field, value)

    db.commit()
    db.refresh(asset_type)
    return asset_type


@work_order_types_router.get("", response_model=list[WorkOrderTypeOut])
def list_work_order_types(
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> list[WorkOrderType]:
    return list(
        db.scalars(select(WorkOrderType).where(WorkOrderType.tenant_id == tenant_id).order_by(WorkOrderType.label))
    )


@work_order_types_router.post("", response_model=WorkOrderTypeOut, status_code=status.HTTP_201_CREATED)
def create_work_order_type(
    payload: WorkOrderTypeCreate,
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_manage_roles),
) -> WorkOrderType:
    work_order_type = WorkOrderType(tenant_id=tenant_id, code=payload.code, label=payload.label)
    db.add(work_order_type)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ya existe un tipo de trabajo con ese código"
        ) from None
    db.refresh(work_order_type)
    return work_order_type


@work_order_types_router.patch("/{work_order_type_id}", response_model=WorkOrderTypeOut)
def update_work_order_type(
    work_order_type_id: uuid.UUID,
    payload: WorkOrderTypeUpdate,
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_manage_roles),
) -> WorkOrderType:
    work_order_type = db.scalar(
        select(WorkOrderType).where(WorkOrderType.id == work_order_type_id, WorkOrderType.tenant_id == tenant_id)
    )
    if work_order_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de trabajo no encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(work_order_type, field, value)

    db.commit()
    db.refresh(work_order_type)
    return work_order_type


@priorities_router.get("", response_model=list[PriorityOut])
def list_priorities(
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> list[Priority]:
    return list(db.scalars(select(Priority).where(Priority.tenant_id == tenant_id).order_by(Priority.sort_order)))


@priorities_router.post("", response_model=PriorityOut, status_code=status.HTTP_201_CREATED)
def create_priority(
    payload: PriorityCreate,
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_manage_roles),
) -> Priority:
    priority = Priority(
        tenant_id=tenant_id, code=payload.code, label=payload.label, sort_order=payload.sort_order
    )
    db.add(priority)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una prioridad con ese código") from None
    db.refresh(priority)
    return priority


@priorities_router.patch("/{priority_id}", response_model=PriorityOut)
def update_priority(
    priority_id: uuid.UUID,
    payload: PriorityUpdate,
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_manage_roles),
) -> Priority:
    priority = db.scalar(select(Priority).where(Priority.id == priority_id, Priority.tenant_id == tenant_id))
    if priority is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prioridad no encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(priority, field, value)

    db.commit()
    db.refresh(priority)
    return priority


@work_order_statuses_router.get("", response_model=list[WorkOrderStatusOut])
def list_work_order_statuses(
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> list[WorkOrderStatus]:
    return list(
        db.scalars(
            select(WorkOrderStatus).where(WorkOrderStatus.tenant_id == tenant_id).order_by(WorkOrderStatus.code)
        )
    )


@work_order_statuses_router.patch("/{work_order_status_id}", response_model=WorkOrderStatusOut)
def update_work_order_status(
    work_order_status_id: uuid.UUID,
    payload: WorkOrderStatusUpdate,
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(_manage_roles),
) -> WorkOrderStatus:
    """Solo permite renombrar `label` o desactivar. `code` es semántica
    interna fija: no se crean ni eliminan estados (modelo-datos.md §4.11).
    """
    work_order_status = db.scalar(
        select(WorkOrderStatus).where(
            WorkOrderStatus.id == work_order_status_id, WorkOrderStatus.tenant_id == tenant_id
        )
    )
    if work_order_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado de OT no encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(work_order_status, field, value)

    db.commit()
    db.refresh(work_order_status)
    return work_order_status
