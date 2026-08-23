import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_tenant_id, require_roles
from app.db.session import get_db
from app.models.asset_type import AssetType
from app.models.location import Asset, Location
from app.models.person import Customer, Person, PersonIdentification, PersonStatus, PersonType, Technician, TechnicianStatus
from app.models.role import TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN
from app.models.user import User
from app.exceptions import TechnicianUserLinkError
from app.schemas.people import (
    AssetCreate,
    AssetOut,
    AssetUpdate,
    CustomerCreate,
    CustomerOut,
    CustomerUpdate,
    LocationCreate,
    LocationOut,
    LocationUpdate,
    PersonIdentificationCreate,
    TechnicianCreate,
    TechnicianLinkUser,
    TechnicianOut,
    TechnicianUpdate,
)
from app.services.people import (
    PersonAlreadyExists,
    PersonNotFound,
    PersonService,
    SpecializationAlreadyExists,
    resolve_or_create_customer,
    resolve_or_create_technician,
)

# Roles que pueden leer clientes/técnicos/ubicaciones/activos
_read_roles = require_roles(TENANT_ADMIN, TENANT_OFFICE, TENANT_TECHNICIAN)
# Roles que pueden gestionar (crear/editar)
_manage_roles = require_roles(TENANT_ADMIN, TENANT_OFFICE)

customers_router = APIRouter(prefix="/customers", tags=["customers"])
technicians_router = APIRouter(prefix="/technicians", tags=["technicians"])
locations_router = APIRouter(prefix="/locations", tags=["locations"])
assets_router = APIRouter(prefix="/assets", tags=["assets"])


# =========================================================================
# CUSTOMERS
# =========================================================================

@customers_router.get("", response_model=list[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[CustomerOut]:
    """Lista clientes del tenant con sus datos de persona."""
    service = PersonService(db)
    customers = service.list_customers(tenant_id)
    result = []
    for c in customers[skip : skip + limit]:
        identifications = service.get_person_identifications(c.person_id)
        result.append(CustomerOut.from_person(c.person, identifications))
    return result


@customers_router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> CustomerOut:
    """Crea un cliente nuevo o reutiliza una Person existente por identificación.

    Flujo transparente:
    1. Busca Person por identificación dentro del tenant
    2. Si no existe: crea Person + identificaciones + Customer
    3. Si existe y no tiene Customer: actualiza datos de Person y crea Customer
    4. Si existe y ya tiene Customer: error 409
    """
    try:
        identifications = [
            PersonIdentification(
                tenant_id=tenant_id,
                person_id=uuid.uuid4(),  # temporal, se reemplaza en service
                country_code=ident.country_code,
                identification_type=ident.identification_type,
                identification_value=ident.identification_value,
                is_primary=ident.is_primary,
            )
            for ident in payload.identifications
        ]
        person, customer, person_created = resolve_or_create_customer(
            db=db,
            tenant_id=tenant_id,
            person_type=payload.person_type,
            display_name=payload.display_name,
            address=payload.address,
            phone=payload.phone,
            email=payload.email,
            notes=payload.notes,
            identifications=identifications,
            created_by=current_user.id,
        )
        db.commit()
    except SpecializationAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La persona ya está registrada como {exc.specialization}",
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error de integridad: posible identificación duplicada",
        ) from exc

    # Recargar con identificaciones para respuesta
    db.refresh(person)
    service = PersonService(db)
    identifications = service.get_person_identifications(person.id)
    return CustomerOut.from_person(person, identifications)


@customers_router.get("/{person_id}", response_model=CustomerOut)
def get_customer(
    person_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> CustomerOut:
    """Obtiene un cliente por person_id (PK compuesta tenant_id + person_id)."""
    service = PersonService(db)
    customer = service.get_customer_with_person(tenant_id, person_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    identifications = service.get_person_identifications(person_id)
    return CustomerOut.from_person(customer.person, identifications)


@customers_router.patch("/{person_id}", response_model=CustomerOut)
def update_customer(
    person_id: uuid.UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> CustomerOut:
    """Actualiza los datos comunes de Person desde la ficha de Cliente."""
    service = PersonService(db)
    customer = service.get_customer_with_person(tenant_id, person_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    person = service.update_person(
        customer.person,
        person_type=payload.person_type,
        display_name=payload.display_name,
        address=payload.address,
        phone=payload.phone,
        email=payload.email,
        notes=payload.notes,
        status=payload.status,
        updated_by=current_user.id,
    )
    db.commit()

    identifications = service.get_person_identifications(person_id)
    return CustomerOut.from_person(person, identifications)


# =========================================================================
# TECHNICIANS
# =========================================================================

@technicians_router.get("", response_model=list[TechnicianOut])
def list_technicians(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(True),
) -> list[TechnicianOut]:
    """Lista técnicos del tenant con sus datos de persona."""
    service = PersonService(db)
    technicians = service.list_technicians(tenant_id)
    if active_only:
        technicians = [t for t in technicians if t.status == TechnicianStatus.ACTIVE]
    result = []
    for t in technicians[skip : skip + limit]:
        identifications = service.get_person_identifications(t.person_id)
        result.append(TechnicianOut.from_person(t.person, t, identifications))
    return result


@technicians_router.post("", response_model=TechnicianOut, status_code=status.HTTP_201_CREATED)
def create_technician(
    payload: TechnicianCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> TechnicianOut:
    """Crea un técnico nuevo o reutiliza una Person existente por identificación.

    Mismo flujo transparente que create_customer pero para Technician.
    """
    try:
        identifications = [
            PersonIdentification(
                tenant_id=tenant_id,
                person_id=uuid.uuid4(),
                country_code=ident.country_code,
                identification_type=ident.identification_type,
                identification_value=ident.identification_value,
                is_primary=ident.is_primary,
            )
            for ident in payload.identifications
        ]
        person, technician, person_created = resolve_or_create_technician(
            db=db,
            tenant_id=tenant_id,
            person_type=payload.person_type,
            display_name=payload.display_name,
            address=payload.address,
            phone=payload.phone,
            email=payload.email,
            notes=payload.notes,
            identifications=identifications,
            profession=payload.profession,
            license_number=payload.license_number,
            commission_percentage=payload.commission_percentage,
            created_by=current_user.id,
        )
        db.commit()
    except SpecializationAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La persona ya está registrada como {exc.specialization}",
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error de integridad: posible identificación duplicada",
        ) from exc

    db.refresh(person)
    service = PersonService(db)
    identifications = service.get_person_identifications(person.id)
    return TechnicianOut.from_person(person, technician, identifications)


@technicians_router.get("/{person_id}", response_model=TechnicianOut)
def get_technician(
    person_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> TechnicianOut:
    """Obtiene un técnico por person_id."""
    service = PersonService(db)
    technician = service.get_technician_with_person(tenant_id, person_id)
    if technician is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Técnico no encontrado")
    identifications = service.get_person_identifications(person_id)
    return TechnicianOut.from_person(technician.person, technician, identifications)


@technicians_router.patch("/{person_id}", response_model=TechnicianOut)
def update_technician(
    person_id: uuid.UUID,
    payload: TechnicianUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> TechnicianOut:
    """Actualiza datos de Person y datos específicos de Technician."""
    service = PersonService(db)
    technician = service.get_technician_with_person(tenant_id, person_id)
    if technician is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Técnico no encontrado")

    # Actualizar Person
    service.update_person(
        technician.person,
        person_type=payload.person_type,
        display_name=payload.display_name,
        address=payload.address,
        phone=payload.phone,
        email=payload.email,
        notes=payload.notes,
        status=payload.status,
        updated_by=current_user.id,
    )

    # Actualizar Technician
    service.update_technician(
        technician,
        profession=payload.profession,
        license_number=payload.license_number,
        commission_percentage=payload.commission_percentage,
        technician_status=payload.technician_status,
        updated_by=current_user.id,
    )

    db.commit()

    identifications = service.get_person_identifications(person_id)
    return TechnicianOut.from_person(technician.person, technician, identifications)


@technicians_router.patch("/{person_id}/user", response_model=TechnicianOut)
def link_technician_user(
    person_id: uuid.UUID,
    payload: TechnicianLinkUser,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> TechnicianOut:
    """Vincula o desvincula (user_id=None) el Técnico con un User de login
    con rol TENANT_TECHNICIAN, habilitando "Mis OT" en el flujo mobile
    (ROADMAP §06)."""
    service = PersonService(db)
    technician = service.get_technician_with_person(tenant_id, person_id)
    if technician is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Técnico no encontrado")

    try:
        service.link_technician_to_user(tenant_id, technician, payload.user_id, updated_by=current_user.id)
        db.commit()
    except TechnicianUserLinkError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    identifications = service.get_person_identifications(person_id)
    return TechnicianOut.from_person(technician.person, technician, identifications)


# =========================================================================
# LOCATIONS
# =========================================================================

@locations_router.get("", response_model=list[LocationOut])
def list_locations(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
    customer_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[Location]:
    """Lista ubicaciones del tenant, opcionalmente filtradas por cliente."""
    stmt = select(Location).where(Location.tenant_id == tenant_id)
    if customer_id:
        stmt = stmt.where(Location.customer_id == customer_id)
    stmt = stmt.order_by(Location.name).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@locations_router.post("", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> Location:
    """Crea una ubicación para un cliente (validando que pertenezca al tenant)."""
    # Validar que el customer existe y pertenece al tenant
    customer = db.scalar(
        select(Customer).where(Customer.tenant_id == tenant_id, Customer.person_id == payload.customer_id)
    )
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    location = Location(
        tenant_id=tenant_id,
        customer_id=payload.customer_id,
        name=payload.name,
        address=payload.address,
        city=payload.city,
        province=payload.province,
        notes=payload.notes,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(location)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una ubicación con ese nombre para este cliente",
        ) from exc
    db.refresh(location)
    return location


@locations_router.get("/{location_id}", response_model=LocationOut)
def get_location(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> Location:
    location = db.scalar(select(Location).where(Location.id == location_id, Location.tenant_id == tenant_id))
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicación no encontrada")
    return location


@locations_router.patch("/{location_id}", response_model=LocationOut)
def update_location(
    location_id: uuid.UUID,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> Location:
    location = db.scalar(select(Location).where(Location.id == location_id, Location.tenant_id == tenant_id))
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicación no encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    location.updated_by = current_user.id

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una ubicación con ese nombre para este cliente",
        ) from exc
    db.refresh(location)
    return location


# =========================================================================
# ASSETS
# =========================================================================

@assets_router.get("", response_model=list[AssetOut])
def list_assets(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
    location_id: Optional[uuid.UUID] = Query(None),
    asset_type_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[AssetOut]:
    """Lista activos del tenant, opcionalmente filtrados por ubicación o tipo."""
    stmt = (
        select(Asset)
        .where(Asset.tenant_id == tenant_id)
        .join(Location, Asset.location_id == Location.id)
    )
    if location_id:
        stmt = stmt.where(Asset.location_id == location_id)
    if asset_type_id:
        stmt = stmt.where(Asset.asset_type_id == asset_type_id)
    stmt = stmt.order_by(Asset.name).offset(skip).limit(limit)
    assets = list(db.scalars(stmt))

    # Enriquecer con asset_type
    result = []
    for asset in assets:
        asset_type = db.get(AssetType, asset.asset_type_id) if asset.asset_type_id else None
        asset_out = AssetOut.model_validate(asset)
        if asset_type:
            from app.schemas.catalog import AssetTypeOut
            asset_out.asset_type = AssetTypeOut.model_validate(asset_type)
        result.append(asset_out)
    return result


@assets_router.post("", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> AssetOut:
    """Crea un activo en una ubicación (validando pertenencia al tenant)."""
    # Validar que la location existe y pertenece al tenant
    location = db.scalar(select(Location).where(Location.id == payload.location_id, Location.tenant_id == tenant_id))
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicación no encontrada")

    # Validar asset_type si se proporciona
    if payload.asset_type_id:
        asset_type = db.scalar(select(AssetType).where(AssetType.id == payload.asset_type_id, AssetType.tenant_id == tenant_id))
        if asset_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de activo no encontrado")

    asset = Asset(
        tenant_id=tenant_id,
        location_id=payload.location_id,
        asset_type_id=payload.asset_type_id,
        name=payload.name,
        description=payload.description,
        brand=payload.brand,
        model=payload.model,
        serial_number=payload.serial_number,
        internal_code=payload.internal_code,
        qr_code=payload.qr_code,
        notes=payload.notes,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.add(asset)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error de integridad: posible QR duplicado",
        ) from exc
    db.refresh(asset)

    asset_out = AssetOut.model_validate(asset)
    if asset.asset_type_id:
        asset_type = db.get(AssetType, asset.asset_type_id)
        if asset_type:
            from app.schemas.catalog import AssetTypeOut
            asset_out.asset_type = AssetTypeOut.model_validate(asset_type)
    return asset_out


@assets_router.get("/qr/{qr_code}", response_model=AssetOut)
def get_asset_by_qr(
    qr_code: str,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> AssetOut:
    """Resuelve un activo a partir del código QR escaneado (PRD §26,
    ROADMAP §06 — Lectura QR). Nunca expone activos de otro tenant."""
    asset = db.scalar(select(Asset).where(Asset.qr_code == qr_code, Asset.tenant_id == tenant_id))
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activo no encontrado")
    asset_out = AssetOut.model_validate(asset)
    if asset.asset_type_id:
        asset_type = db.get(AssetType, asset.asset_type_id)
        if asset_type:
            from app.schemas.catalog import AssetTypeOut
            asset_out.asset_type = AssetTypeOut.model_validate(asset_type)
    return asset_out


@assets_router.get("/{asset_id}", response_model=AssetOut)
def get_asset(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    _: User = Depends(_read_roles),
) -> AssetOut:
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.tenant_id == tenant_id))
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activo no encontrado")
    asset_out = AssetOut.model_validate(asset)
    if asset.asset_type_id:
        asset_type = db.get(AssetType, asset.asset_type_id)
        if asset_type:
            from app.schemas.catalog import AssetTypeOut
            asset_out.asset_type = AssetTypeOut.model_validate(asset_type)
    return asset_out


@assets_router.patch("/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: uuid.UUID,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(_manage_roles),
) -> AssetOut:
    asset = db.scalar(select(Asset).where(Asset.id == asset_id, Asset.tenant_id == tenant_id))
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activo no encontrado")

    # Validar asset_type si se proporciona
    if payload.asset_type_id:
        asset_type = db.scalar(select(AssetType).where(AssetType.id == payload.asset_type_id, AssetType.tenant_id == tenant_id))
        if asset_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de activo no encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    asset.updated_by = current_user.id

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error de integridad: posible QR duplicado",
        ) from exc
    db.refresh(asset)

    asset_out = AssetOut.model_validate(asset)
    if asset.asset_type_id:
        asset_type = db.get(AssetType, asset.asset_type_id)
        if asset_type:
            from app.schemas.catalog import AssetTypeOut
            asset_out.asset_type = AssetTypeOut.model_validate(asset_type)
    return asset_out