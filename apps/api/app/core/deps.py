import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.rls import set_authenticated_context, set_user_identity_context
from app.db.session import get_db
from app.models.role import PLATFORM_OWNER
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resuelve el usuario autenticado a partir del token firmado por el
    backend. El `tenant_id` de contexto se deriva SIEMPRE de este usuario,
    nunca de un valor enviado por el cliente (arquitectura.md §3.2).
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error

    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError:
        raise credentials_error from None

    set_user_identity_context(db, parsed_user_id)
    user = db.get(User, parsed_user_id)

    if user is None or not user.is_active:
        raise credentials_error

    set_authenticated_context(
        db,
        tenant_id=user.tenant_id,
        is_platform_admin=user.role.code == PLATFORM_OWNER,
    )

    return user


def get_current_tenant_id(current_user: User = Depends(get_current_user)) -> uuid.UUID:
    """Tenant activo de la request, resuelto server-side. Los endpoints
    tenant-scoped dependen de esto en lugar de aceptar `tenant_id` por
    parámetro (decisiones-producto.md §11).
    """
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este usuario no pertenece a un tenant",
        )
    return current_user.tenant_id


def require_roles(*allowed_codes: str) -> Callable[[User], User]:
    """Dependencia RBAC: exige que el usuario autenticado tenga uno de los
    roles indicados. La verificación ocurre siempre en backend (PRD §21).
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.code not in allowed_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para esta operación",
            )
        return current_user

    return checker
