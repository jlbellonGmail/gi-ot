"""Capa de servicio/dominio para el módulo People.

Implementa la lógica de negocio para búsqueda/creación de Person y sus
especializaciones (Customer, Technician) siguiendo el flujo transparente
definido en modelo-datos.md §10 y decisiones-producto.md §16.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import TechnicianUserLinkError
from app.models.person import Customer, Person, PersonIdentification, PersonStatus, PersonType, Technician, TechnicianStatus
from app.models.role import TENANT_TECHNICIAN
from app.models.user import User


class PersonAlreadyExists(Exception):
    """La Person ya existe para la identificación dada en el tenant."""
    def __init__(self, person: Person):
        self.person = person
        super().__init__(f"Persona ya existe con id {person.id}")


class SpecializationAlreadyExists(Exception):
    """La especialización solicitada ya existe para esta Person."""
    def __init__(self, specialization: str):
        self.specialization = specialization
        super().__init__(f"La especialización '{specialization}' ya existe para esta persona")


class PersonNotFound(Exception):
    """No se encontró la Person solicitada."""
    pass


class PersonService:
    """Servicio de dominio para operaciones sobre Person y especializaciones."""

    def __init__(self, db: Session):
        self.db = db

    def _normalize_identification_value(self, value: str) -> str:
        """Normaliza el valor de identificación quitando espacios, guiones, etc."""
        return "".join(value.split()).replace("-", "").replace(".", "").upper()

    def find_person_by_identification(
        self,
        tenant_id: uuid.UUID,
        country_code: str,
        identification_type: str,
        identification_value: str,
    ) -> Optional[Person]:
        """Busca una Person por identificación dentro del tenant.

        Retorna la Person si existe, None si no existe.
        """
        normalized_value = self._normalize_identification_value(identification_value)

        stmt = (
            select(Person)
            .join(PersonIdentification, PersonIdentification.person_id == Person.id)
            .where(
                Person.tenant_id == tenant_id,
                PersonIdentification.country_code == country_code.upper(),
                PersonIdentification.identification_type == identification_type.upper(),
                PersonIdentification.identification_value == normalized_value,
            )
        )
        return self.db.scalar(stmt)

    def create_person_with_identification(
        self,
        tenant_id: uuid.UUID,
        person_type: PersonType,
        display_name: str,
        address: Optional[str],
        phone: Optional[str],
        email: Optional[str],
        notes: Optional[str],
        identifications: list[PersonIdentification],
        created_by: Optional[uuid.UUID] = None,
    ) -> Person:
        """Crea una Person con sus identificaciones en una sola transacción."""
        person = Person(
            tenant_id=tenant_id,
            person_type=person_type,
            display_name=display_name,
            address=address,
            phone=phone,
            email=email,
            notes=notes,
            status=PersonStatus.ACTIVE,
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(person)
        self.db.flush()

        for ident in identifications:
            normalized_value = self._normalize_identification_value(ident.identification_value)
            person_ident = PersonIdentification(
                tenant_id=tenant_id,
                person_id=person.id,
                country_code=ident.country_code.upper(),
                identification_type=ident.identification_type.upper(),
                identification_value=normalized_value,
                is_primary=ident.is_primary,
            )
            self.db.add(person_ident)

        self.db.flush()
        return person

    def add_identification_to_person(
        self,
        person: Person,
        country_code: str,
        identification_type: str,
        identification_value: str,
        is_primary: bool = False,
    ) -> PersonIdentification:
        """Agrega una identificación a una Person existente."""
        normalized_value = self._normalize_identification_value(identification_value)

        ident = PersonIdentification(
            tenant_id=person.tenant_id,
            person_id=person.id,
            country_code=country_code.upper(),
            identification_type=identification_type.upper(),
            identification_value=normalized_value,
            is_primary=is_primary,
        )
        self.db.add(ident)
        self.db.flush()
        return ident

    def create_customer(
        self,
        tenant_id: uuid.UUID,
        person: Person,
        created_by: Optional[uuid.UUID] = None,
    ) -> Customer:
        """Crea la especialización Customer para una Person existente."""
        # Verificar en BD para evitar race conditions y no depender de lazy loading
        existing = self.db.scalar(
            select(Customer).where(Customer.tenant_id == tenant_id, Customer.person_id == person.id)
        )
        if existing is not None:
            raise SpecializationAlreadyExists("Customer")

        customer = Customer(
            tenant_id=tenant_id,
            person_id=person.id,
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(customer)
        self.db.flush()
        return customer

    def create_technician(
        self,
        tenant_id: uuid.UUID,
        person: Person,
        profession: Optional[str] = None,
        license_number: Optional[str] = None,
        commission_percentage: Optional[float] = None,
        created_by: Optional[uuid.UUID] = None,
    ) -> Technician:
        """Crea la especialización Technician para una Person existente."""
        existing = self.db.scalar(
            select(Technician).where(Technician.tenant_id == tenant_id, Technician.person_id == person.id)
        )
        if existing is not None:
            raise SpecializationAlreadyExists("Technician")

        technician = Technician(
            tenant_id=tenant_id,
            person_id=person.id,
            profession=profession,
            license_number=license_number,
            commission_percentage=commission_percentage,
            status=TechnicianStatus.ACTIVE,
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(technician)
        self.db.flush()
        return technician

    def update_person(
        self,
        person: Person,
        person_type: Optional[PersonType] = None,
        display_name: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[PersonStatus] = None,
        updated_by: Optional[uuid.UUID] = None,
    ) -> Person:
        """Actualiza los datos comunes de una Person."""
        if person_type is not None:
            person.person_type = person_type
        if display_name is not None:
            person.display_name = display_name
        if address is not None:
            person.address = address
        if phone is not None:
            person.phone = phone
        if email is not None:
            person.email = email
        if notes is not None:
            person.notes = notes
        if status is not None:
            person.status = status

        person.updated_by = updated_by
        person.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return person

    def update_technician(
        self,
        technician: Technician,
        profession: Optional[str] = None,
        license_number: Optional[str] = None,
        commission_percentage: Optional[float] = None,
        technician_status: Optional[TechnicianStatus] = None,
        updated_by: Optional[uuid.UUID] = None,
    ) -> Technician:
        """Actualiza los datos específicos de un Technician."""
        if profession is not None:
            technician.profession = profession
        if license_number is not None:
            technician.license_number = license_number
        if commission_percentage is not None:
            technician.commission_percentage = commission_percentage
        if technician_status is not None:
            technician.status = technician_status

        technician.updated_by = updated_by
        technician.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return technician

    def link_technician_to_user(
        self,
        tenant_id: uuid.UUID,
        technician: Technician,
        user_id: Optional[uuid.UUID],
        updated_by: Optional[uuid.UUID] = None,
    ) -> Technician:
        """Vincula (o desvincula, si user_id es None) un Technician con un
        User de login. Valida que el User exista, pertenezca al tenant,
        tenga rol TENANT_TECHNICIAN y no esté ya vinculado a otro Technician
        (ROADMAP §06 — vínculo necesario para "Mis OT")."""
        if user_id is not None:
            user = self.db.get(User, user_id)
            if user is None or user.tenant_id != tenant_id:
                raise TechnicianUserLinkError("El usuario no existe en este tenant")
            if user.role.code != TENANT_TECHNICIAN:
                raise TechnicianUserLinkError("El usuario no tiene rol TENANT_TECHNICIAN")
            already_linked = self.db.scalar(
                select(Technician).where(
                    Technician.tenant_id == tenant_id,
                    Technician.user_id == user_id,
                    Technician.person_id != technician.person_id,
                )
            )
            if already_linked is not None:
                raise TechnicianUserLinkError("El usuario ya está vinculado a otro técnico")

        technician.user_id = user_id
        technician.updated_by = updated_by
        technician.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return technician

    def get_customer_with_person(self, tenant_id: uuid.UUID, person_id: uuid.UUID) -> Optional[Customer]:
        """Obtiene un Customer con su Person asociada, validando tenant."""
        stmt = (
            select(Customer)
            .join(Person)
            .where(
                Customer.tenant_id == tenant_id,
                Customer.person_id == person_id,
                Person.tenant_id == tenant_id,
            )
        )
        return self.db.scalar(stmt)

    def get_technician_with_person(self, tenant_id: uuid.UUID, person_id: uuid.UUID) -> Optional[Technician]:
        """Obtiene un Technician con su Person asociada, validando tenant."""
        stmt = (
            select(Technician)
            .join(Person)
            .where(
                Technician.tenant_id == tenant_id,
                Technician.person_id == person_id,
                Person.tenant_id == tenant_id,
            )
        )
        return self.db.scalar(stmt)

    def list_customers(self, tenant_id: uuid.UUID) -> list[Customer]:
        """Lista todos los Customers del tenant con su Person."""
        stmt = (
            select(Customer)
            .join(Person)
            .where(Customer.tenant_id == tenant_id, Person.tenant_id == tenant_id)
            .order_by(Person.display_name)
        )
        return list(self.db.scalars(stmt))

    def list_technicians(self, tenant_id: uuid.UUID) -> list[Technician]:
        """Lista todos los Technicians del tenant con su Person."""
        stmt = (
            select(Technician)
            .join(Person)
            .where(Technician.tenant_id == tenant_id, Person.tenant_id == tenant_id)
            .order_by(Person.display_name)
        )
        return list(self.db.scalars(stmt))

    def get_person_identifications(self, person_id: uuid.UUID) -> list[PersonIdentification]:
        """Obtiene todas las identificaciones de una Person."""
        stmt = select(PersonIdentification).where(PersonIdentification.person_id == person_id)
        return list(self.db.scalars(stmt))


def resolve_or_create_customer(
    db: Session,
    tenant_id: uuid.UUID,
    person_type: PersonType,
    display_name: str,
    address: Optional[str],
    phone: Optional[str],
    email: Optional[str],
    notes: Optional[str],
    identifications: list[PersonIdentification],
    created_by: Optional[uuid.UUID] = None,
) -> tuple[Person, Customer, bool]:
    """Operación de alto nivel: busca Person por identificación o crea Person+Customer.

    Retorna: (person, customer, person_was_created)
    - person_was_created = True si se creó una Person nueva
    - person_was_created = False si la Person ya existía (y se agregó Customer si no la tenía)

    Lanza SpecializationAlreadyExists si la Person ya tiene Customer.
    """
    service = PersonService(db)

    # Buscar por la primera identificación (la primaria)
    primary_ident = identifications[0]
    existing_person = service.find_person_by_identification(
        tenant_id=tenant_id,
        country_code=primary_ident.country_code,
        identification_type=primary_ident.identification_type,
        identification_value=primary_ident.identification_value,
    )

    if existing_person is None:
        # Person no existe -> crear Person + identificaciones + Customer
        person = service.create_person_with_identification(
            tenant_id=tenant_id,
            person_type=person_type,
            display_name=display_name,
            address=address,
            phone=phone,
            email=email,
            notes=notes,
            identifications=identifications,
            created_by=created_by,
        )
        customer = service.create_customer(tenant_id=tenant_id, person=person, created_by=created_by)
        return person, customer, True

    # Person existe - verificar si ya tiene Customer en BD (no confiar en lazy loading)
    existing_customer = service.get_customer_with_person(tenant_id, existing_person.id)
    if existing_customer is not None:
        # Ya es Customer -> error, no duplicar
        raise SpecializationAlreadyExists("Customer")

    # Agregar identificaciones adicionales que no existan
    existing_idents = {(i.country_code, i.identification_type, i.identification_value) for i in existing_person.identifications}
    for ident in identifications:
        normalized_value = service._normalize_identification_value(ident.identification_value)
        key = (ident.country_code.upper(), ident.identification_type.upper(), normalized_value)
        if key not in existing_idents:
            service.add_identification_to_person(
                existing_person,
                ident.country_code,
                ident.identification_type,
                ident.identification_value,
                ident.is_primary,
            )

    # Actualizar datos comunes si se proporcionaron (opcional, según política de negocio)
    # En el MVP, si el usuario ingresó nuevos datos, los actualizamos
    service.update_person(
        existing_person,
        person_type=person_type,
        display_name=display_name,
        address=address,
        phone=phone,
        email=email,
        notes=notes,
        updated_by=created_by,
    )

    # Crear Customer
    customer = service.create_customer(tenant_id=tenant_id, person=existing_person, created_by=created_by)
    return existing_person, customer, False


def resolve_or_create_technician(
    db: Session,
    tenant_id: uuid.UUID,
    person_type: PersonType,
    display_name: str,
    address: Optional[str],
    phone: Optional[str],
    email: Optional[str],
    notes: Optional[str],
    identifications: list[PersonIdentification],
    profession: Optional[str] = None,
    license_number: Optional[str] = None,
    commission_percentage: Optional[float] = None,
    created_by: Optional[uuid.UUID] = None,
) -> tuple[Person, Technician, bool]:
    """Operación de alto nivel: busca Person por identificación o crea Person+Technician.

    Retorna: (person, technician, person_was_created)
    - person_was_created = True si se creó una Person nueva
    - person_was_created = False si la Person ya existía (y se agregó Technician si no la tenía)

    Lanza SpecializationAlreadyExists si la Person ya tiene Technician.
    """
    service = PersonService(db)

    # Buscar por la primera identificación
    primary_ident = identifications[0]
    existing_person = service.find_person_by_identification(
        tenant_id=tenant_id,
        country_code=primary_ident.country_code,
        identification_type=primary_ident.identification_type,
        identification_value=primary_ident.identification_value,
    )

    if existing_person is None:
        # Person no existe -> crear Person + identificaciones + Technician
        person = service.create_person_with_identification(
            tenant_id=tenant_id,
            person_type=person_type,
            display_name=display_name,
            address=address,
            phone=phone,
            email=email,
            notes=notes,
            identifications=identifications,
            created_by=created_by,
        )
        technician = service.create_technician(
            tenant_id=tenant_id,
            person=person,
            profession=profession,
            license_number=license_number,
            commission_percentage=commission_percentage,
            created_by=created_by,
        )
        return person, technician, True

    # Person existe
    # Verificar si ya tiene Technician en BD (no confiar en lazy loading)
    existing_technician = service.get_technician_with_person(tenant_id, existing_person.id)
    if existing_technician is not None:
        # Ya es Technician -> error
        raise SpecializationAlreadyExists("Technician")

    # Agregar identificaciones adicionales que no existan
    existing_idents = {(i.country_code, i.identification_type, i.identification_value) for i in existing_person.identifications}
    for ident in identifications:
        normalized_value = service._normalize_identification_value(ident.identification_value)
        key = (ident.country_code.upper(), ident.identification_type.upper(), normalized_value)
        if key not in existing_idents:
            service.add_identification_to_person(
                existing_person,
                ident.country_code,
                ident.identification_type,
                ident.identification_value,
                ident.is_primary,
            )

    # Actualizar datos comunes
    service.update_person(
        existing_person,
        person_type=person_type,
        display_name=display_name,
        address=address,
        phone=phone,
        email=email,
        notes=notes,
        updated_by=created_by,
    )

    # Crear Technician
    technician = service.create_technician(
        tenant_id=tenant_id,
        person=existing_person,
        profession=profession,
        license_number=license_number,
        commission_percentage=commission_percentage,
        created_by=created_by,
    )
    return existing_person, technician, False
