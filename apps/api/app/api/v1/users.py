import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_tenant_id, require_roles
from app.core.security import hash_password
from app.db.session import get_db
from app.models.role import ALL_ROLE_CODES, PLATFORM_OWNER, TENANT_ADMIN, Role
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


def _to_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role_code=user.role.code,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(require_roles(TENANT_ADMIN)),
) -> list[UserOut]:
    # Filtro obligatorio por tenant de contexto: nunca se acepta un
    # tenant_id externo (arquitectura.md §3.3).
    users = db.scalars(select(User).where(User.tenant_id == tenant_id)).all()
    return [_to_out(u) for u in users]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(require_roles(TENANT_ADMIN)),
) -> UserOut:
    if payload.role_code == PLATFORM_OWNER or payload.role_code not in ALL_ROLE_CODES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rol inválido")

    role = db.scalar(select(Role).where(Role.code == payload.role_code))
    if role is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Rol no inicializado")

    existing = db.scalar(
        select(User).where(User.tenant_id == tenant_id, User.email == payload.email)
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ya registrado en el tenant")

    user = User(
        tenant_id=tenant_id,
        role_id=role.id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_out(user)
