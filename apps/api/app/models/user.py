import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.tenant import Tenant


class User(Base):
    """Cuenta de acceso. `tenant_id` es nulo únicamente para PLATFORM_OWNER
    (modelo-datos.md §4.3): ningún otro rol existe sin tenant.

    Dos índices únicos parciales cubren la regla de unicidad de email
    (decisiones-producto.md): dentro de un tenant (`tenant_id` no nulo) por
    la restricción compuesta; a nivel plataforma (`tenant_id` nulo, es decir
    PLATFORM_OWNER) por el índice parcial dedicado, porque un UNIQUE
    compuesto normal trata cada NULL como distinto y no evitaría duplicados
    entre PLATFORM_OWNER. Ambos índices son válidos en SQLite y PostgreSQL.
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_users_tenant_id"),
        Index(
            "ix_users_tenant_email",
            "tenant_id",
            "email",
            unique=True,
            sqlite_where=text("tenant_id IS NOT NULL"),
            postgresql_where=text("tenant_id IS NOT NULL"),
        ),
        Index(
            "ix_users_platform_owner_email",
            "email",
            unique=True,
            sqlite_where=text("tenant_id IS NULL"),
            postgresql_where=text("tenant_id IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    tenant: Mapped["Tenant | None"] = relationship()
    role: Mapped["Role"] = relationship()
