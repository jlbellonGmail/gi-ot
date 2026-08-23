import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, ForeignKeyConstraint, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PersonType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    LEGAL = "LEGAL"


class PersonStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Person(Base):
    """Entidad base compartida por todas las especializaciones de negocio
    (Customer, Technician, y futuras). Contiene los datos generales de una
    persona física o jurídica una sola vez por tenant (§4.5, §10 modelo-datos.md).
    """

    __tablename__ = "people"
    __table_args__ = (
        Index("ix_people_display_name", "tenant_id", "display_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    person_type: Mapped[PersonType] = mapped_column(
        SQLEnum(PersonType, native_enum=False), nullable=False, default=PersonType.INDIVIDUAL
    )
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PersonStatus] = mapped_column(
        SQLEnum(PersonStatus, native_enum=False), nullable=False, default=PersonStatus.ACTIVE
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    identifications: Mapped[list["PersonIdentification"]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )
    customer: Mapped["Customer | None"] = relationship(
        back_populates="person", uselist=False, cascade="all, delete-orphan"
    )
    technician: Mapped["Technician | None"] = relationship(
        back_populates="person", uselist=False, cascade="all, delete-orphan"
    )


class PersonIdentification(Base):
    """Identificaciones de una Person (documento nacional, identificación
    tributaria, u otro según país). Nunca se usa como PK técnica.
    Unicidad por (tenant_id, country_code, identification_type, identification_value)
    para prevenir duplicados dentro del tenant (§4.6, §10.4 modelo-datos.md).
    """

    __tablename__ = "person_identifications"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "country_code", "identification_type", "identification_value",
            name="uq_person_identifications_tenant_country_type_value"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)  # ISO 3166-1 alpha-2
    identification_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ej: DNI, CUIT, NIF, RUT
    identification_value: Mapped[str] = mapped_column(String(50), nullable=False)  # valor normalizado
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    person: Mapped["Person"] = relationship(back_populates="identifications")


class Customer(Base):
    """Especialización de Person para el rol comercial de cliente.
    Clave compuesta (tenant_id, person_id) — PK y FK simultánea hacia Person.
    No duplica display_name, address, phone, email (§4.7, §10.3 modelo-datos.md).
    """

    __tablename__ = "customers"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "person_id"],
            ["people.tenant_id", "people.id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True, nullable=False, index=True
    )
    person_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    person: Mapped["Person"] = relationship(back_populates="customer", foreign_keys=[person_id])
    locations: Mapped[list["Location"]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class TechnicianStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Technician(Base):
    """Especialización de Person para el rol operativo de técnico.
    Clave compuesta (tenant_id, person_id) — PK y FK simultánea hacia Person.
    Independiente de User/rol RBAC (§4.8, §10.9 modelo-datos.md).
    """

    __tablename__ = "technicians"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "person_id"],
            ["people.tenant_id", "people.id"],
            ondelete="CASCADE",
        ),
        Index("ix_technicians_status", "tenant_id", "status"),
        Index("ix_technicians_user_id", "user_id", unique=True),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True, nullable=False, index=True
    )
    person_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, nullable=False)
    profession: Mapped[str | None] = mapped_column(String(100), nullable=True)
    license_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    commission_percentage: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[TechnicianStatus] = mapped_column(
        SQLEnum(TechnicianStatus, native_enum=False), nullable=False, default=TechnicianStatus.ACTIVE
    )
    # Vínculo opcional hacia el User (login) con rol TENANT_TECHNICIAN que
    # opera este Technician en el flujo mobile ("Mis OT" — ROADMAP §06).
    # Se asigna desde la ficha de técnico existente, no en el alta.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    person: Mapped["Person"] = relationship(back_populates="technician", foreign_keys=[person_id])