from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_tenant_id, require_roles
from app.db.session import get_db
from app.models.role import TENANT_ADMIN, TENANT_OFFICE
from app.models.tenant import TenantConfig
from app.models.user import User
from app.schemas.tenant import TenantConfigOut, TenantConfigUpdate

router = APIRouter(prefix="/tenant-config", tags=["tenant-config"])


@router.get("", response_model=TenantConfigOut)
def get_tenant_config(
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(require_roles(TENANT_ADMIN, TENANT_OFFICE)),
) -> TenantConfig:
    config = db.scalar(select(TenantConfig).where(TenantConfig.tenant_id == tenant_id))
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    return config


@router.patch("", response_model=TenantConfigOut)
def update_tenant_config(
    payload: TenantConfigUpdate,
    db: Session = Depends(get_db),
    tenant_id=Depends(get_current_tenant_id),
    _: User = Depends(require_roles(TENANT_ADMIN)),
) -> TenantConfig:
    config = db.scalar(select(TenantConfig).where(TenantConfig.tenant_id == tenant_id))
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(config, field, value)

    db.commit()
    db.refresh(config)
    return config
