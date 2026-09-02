"""Crea el primer usuario PLATFORM_OWNER (sin tenant).

Uso:
    python scripts/create_platform_owner.py <email> <password> "<Nombre completo>"

Solo necesario una vez por entorno: no hay UI para esto en el MVP porque
PLATFORM_OWNER no pertenece a ningún tenant (modelo-funcional.md §3).
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.role import PLATFORM_OWNER, Role
from app.models.user import User
from sqlalchemy import select


def main() -> None:
    if len(sys.argv) != 4:
        print(__doc__)
        raise SystemExit(1)

    email, password, full_name = sys.argv[1], sys.argv[2], sys.argv[3]

    db = SessionLocal()
    try:
        role = db.scalar(select(Role).where(Role.code == PLATFORM_OWNER))
        if role is None:
            raise SystemExit("El catálogo de roles no está inicializado: ejecutar alembic upgrade head")

        existing = db.scalar(select(User).where(User.email == email, User.tenant_id.is_(None)))
        if existing is not None:
            raise SystemExit(f"Ya existe un PLATFORM_OWNER con email {email}")

        user = User(
            tenant_id=None,
            role_id=role.id,
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        print(f"PLATFORM_OWNER creado: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
