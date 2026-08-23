import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PersonType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    LEGAL = "LEGAL"


class PersonStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class TechnicianStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class AssetStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"


# --- PersonIdentification schemas ---
class PersonIdentificationBase(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    identification_type: str = Field(min_length=1, max_length=50)
    identification_value: str = Field(min_length=1, max_length=50)
    is_primary: bool = False


class PersonIdentificationCreate(PersonIdentificationBase):
    pass


class PersonIdentificationOut(PersonIdentificationBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    person_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Person schemas (internal, not directly exposed to frontend) ---
class PersonBase(BaseModel):
    person_type: PersonType = PersonType.INDIVIDUAL
    display_name: str = Field(min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None
    status: PersonStatus = PersonStatus.ACTIVE


class PersonCreate(PersonBase):
    identifications: list[PersonIdentificationCreate] = Field(default_factory=list)


class PersonUpdate(BaseModel):
    person_type: Optional[PersonType] = None
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None
    status: Optional[PersonStatus] = None


class PersonOut(PersonBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    identifications: list[PersonIdentificationOut] = []

    model_config = ConfigDict(from_attributes=True)


# --- Customer schemas ---
class CustomerBase(BaseModel):
    pass  # No own fields in MVP; all data comes from Person


class CustomerCreate(BaseModel):
    """Datos para crear un Cliente: datos de Persona + identificación + datos específicos de Cliente (vacío en MVP)."""
    person_type: PersonType = PersonType.INDIVIDUAL
    display_name: str = Field(min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None
    identifications: list[PersonIdentificationCreate] = Field(min_length=1)


class CustomerUpdate(BaseModel):
    """Actualización de datos comunes de Persona desde la ficha de Cliente."""
    person_type: Optional[PersonType] = None
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None
    status: Optional[PersonStatus] = None


class CustomerOut(BaseModel):
    tenant_id: uuid.UUID
    person_id: uuid.UUID
    display_name: str
    person_type: PersonType
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    status: PersonStatus
    identifications: list[PersonIdentificationOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_person(cls, person, identifications=None):
        return cls(
            tenant_id=person.tenant_id,
            person_id=person.id,
            display_name=person.display_name,
            person_type=person.person_type,
            address=person.address,
            phone=person.phone,
            email=person.email,
            notes=person.notes,
            status=person.status,
            identifications=identifications or [],
            created_at=person.created_at,
            updated_at=person.updated_at,
        )


# --- Technician schemas ---
class TechnicianBase(BaseModel):
    profession: Optional[str] = Field(default=None, max_length=100)
    license_number: Optional[str] = Field(default=None, max_length=50)
    commission_percentage: Optional[float] = None


class TechnicianCreate(BaseModel):
    """Datos para crear un Técnico: datos de Persona + identificación + datos específicos de Técnico."""
    person_type: PersonType = PersonType.INDIVIDUAL
    display_name: str = Field(min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None
    identifications: list[PersonIdentificationCreate] = Field(min_length=1)
    profession: Optional[str] = Field(default=None, max_length=100)
    license_number: Optional[str] = Field(default=None, max_length=50)
    commission_percentage: Optional[float] = None


class TechnicianUpdate(BaseModel):
    """Actualización de datos de Persona + datos específicos de Técnico."""
    person_type: Optional[PersonType] = None
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None
    status: Optional[PersonStatus] = None
    profession: Optional[str] = Field(default=None, max_length=100)
    license_number: Optional[str] = Field(default=None, max_length=50)
    commission_percentage: Optional[float] = None
    technician_status: Optional[TechnicianStatus] = None


class TechnicianLinkUser(BaseModel):
    """Vincula o desvincula (user_id=None) el Technician con un User de
    login con rol TENANT_TECHNICIAN (ROADMAP §06 — habilita "Mis OT")."""
    user_id: Optional[uuid.UUID] = None


class TechnicianOut(BaseModel):
    tenant_id: uuid.UUID
    person_id: uuid.UUID
    display_name: str
    person_type: PersonType
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    status: PersonStatus
    identifications: list[PersonIdentificationOut] = []
    profession: Optional[str] = None
    license_number: Optional[str] = None
    commission_percentage: Optional[float] = None
    technician_status: TechnicianStatus
    user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_person(cls, person, technician, identifications=None):
        return cls(
            tenant_id=person.tenant_id,
            person_id=person.id,
            display_name=person.display_name,
            person_type=person.person_type,
            address=person.address,
            phone=person.phone,
            email=person.email,
            notes=person.notes,
            status=person.status,
            identifications=identifications or [],
            profession=technician.profession,
            license_number=technician.license_number,
            commission_percentage=technician.commission_percentage,
            technician_status=technician.status,
            user_id=technician.user_id,
            created_at=person.created_at,
            updated_at=person.updated_at,
        )


# --- Location schemas ---
class LocationBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None


class LocationCreate(LocationBase):
    customer_id: uuid.UUID


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None


class LocationOut(LocationBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    customer_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Asset schemas ---
class AssetBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100)
    internal_code: Optional[str] = Field(default=None, max_length=50)
    qr_code: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None
    asset_type_id: Optional[uuid.UUID] = None


class AssetCreate(AssetBase):
    location_id: uuid.UUID


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    serial_number: Optional[str] = Field(default=None, max_length=100)
    internal_code: Optional[str] = Field(default=None, max_length=50)
    qr_code: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None
    asset_type_id: Optional[uuid.UUID] = None
    status: Optional[AssetStatus] = None


class AssetOut(AssetBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    location_id: uuid.UUID
    status: AssetStatus
    created_at: datetime
    updated_at: datetime
    asset_type: Optional["AssetTypeOut"] = None

    model_config = ConfigDict(from_attributes=True)


# Forward reference
from app.schemas.catalog import AssetTypeOut

AssetOut.model_rebuild()