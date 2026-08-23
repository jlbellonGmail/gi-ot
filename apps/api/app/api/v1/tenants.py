import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.core.provisioning import ConfigTemplateNotFound, provision_tenant_from_template
from app.core.security import hash_password
from app.db.session import get_db
from app.models.role import TENANT_ADMIN, PLATFORM_OWNER
from app.models.role import Role
from app.models.tenant import TENANT_ACTIVE, TENANT_SUSPENDED, Tenant, TenantConfig
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantOut, TenantStatusUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])

_platform_owner_only = require_roles(PLATFORM_OWNER)


@router.get("", response_model=list[TenantOut])
def list_tenants(
    db: Session = Depends(get_db),
    _: User = Depends(_platform_owner_only),
) -> list[Tenant]:
    return list(db.scalars(select(Tenant).order_by(Tenant.created_at)))


@router.post("", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_platform_owner_only),
) -> Tenant:
    admin_role = db.scalar(select(Role).where(Role.code == TENANT_ADMIN))
    if admin_role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El catálogo de roles no está inicializado",
        )

    tenant = Tenant(name=payload.name, commercial_name=payload.commercial_name)
    db.add(tenant)
    db.flush()

    db.add(TenantConfig(tenant_id=tenant.id, commercial_display_name=payload.commercial_name))
    try:
        provision_tenant_from_template(db, tenant.id)
    except ConfigTemplateNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La plantilla de configuración inicial no está inicializada",
        ) from exc

    existing = db.scalar(
        select(User).where(User.tenant_id == tenant.id, User.email == payload.admin_email)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email en el tenant",
        )

    db.add(
        User(
            tenant_id=tenant.id,
            role_id=admin_role.id,
            email=payload.admin_email,
            full_name=payload.admin_full_name,
            password_hash=hash_password(payload.admin_password),
        )
    )

    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/{tenant_id}", response_model=TenantOut)
def get_tenant(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(_platform_owner_only),
) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant no encontrado")
    return tenant


@router.patch("/{tenant_id}/status", response_model=TenantOut)
def update_tenant_status(
    tenant_id: uuid.UUID,
    payload: TenantStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_platform_owner_only),
) -> Tenant:
    if payload.status not in (TENANT_ACTIVE, TENANT_SUSPENDED):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Estado inválido")

    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant no encontrado")

    tenant.status = payload.status
    db.commit()
    db.refresh(tenant)
    return tenant
