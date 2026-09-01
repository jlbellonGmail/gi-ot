from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.rls import set_login_context
from app.db.session import get_db
from app.models.person import Technician
from app.models.role import TENANT_TECHNICIAN
from app.models.user import User
from app.schemas.auth import CurrentUser, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    set_login_context(db, payload.email)
    user = db.scalar(select(User).where(User.email == payload.email))

    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUser)
def me(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CurrentUser:
    technician_person_id = None
    if current_user.role.code == TENANT_TECHNICIAN:
        technician = db.scalar(
            select(Technician).where(
                Technician.tenant_id == current_user.tenant_id,
                Technician.user_id == current_user.id,
            )
        )
        if technician is not None:
            technician_person_id = technician.person_id

    return CurrentUser(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role_code=current_user.role.code,
        tenant_id=current_user.tenant_id,
        technician_person_id=technician_person_id,
    )
