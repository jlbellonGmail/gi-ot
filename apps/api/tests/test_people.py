"""Pruebas de la Etapa 03 — Maestros (ROADMAP.md §03).

Cubren: Person, PersonIdentification, Customer, Technician, Location, Asset;
flujo transparente de alta por identificación; reutilización de Person;
actualización de datos comunes; aislamiento multitenant.
"""

import uuid

from sqlalchemy import select

from app.models.person import Customer, Person, PersonIdentification, PersonType, Technician, TechnicianStatus
from app.services.people import (
    PersonService,
    SpecializationAlreadyExists,
    resolve_or_create_customer,
    resolve_or_create_technician,
)
from tests.helpers import auth_headers, create_platform_owner, create_tenant_via_api, login


def _setup_two_tenants(client, db_session):
    create_platform_owner(db_session)
    owner_token = login(client, "owner@gi-ot.com", "Owner123!")

    tenant_a = create_tenant_via_api(
        client, owner_token, "Servicio Tecnico Cordoba", "admin@stc.com.ar", "AdminA123!"
    )
    tenant_b = create_tenant_via_api(
        client, owner_token, "Ascensores del Litoral", "admin@adl.com.ar", "AdminB123!"
    )

    token_a = login(client, "admin@stc.com.ar", "AdminA123!")
    token_b = login(client, "admin@adl.com.ar", "AdminB123!")

    return owner_token, tenant_a, tenant_b, token_a, token_b


def _create_customer_via_api(client, token, person_data):
    return client.post("/api/v1/customers", headers=auth_headers(token), json=person_data)


def _create_technician_via_api(client, token, person_data):
    return client.post("/api/v1/technicians", headers=auth_headers(token), json=person_data)


def _create_location_via_api(client, token, location_data):
    return client.post("/api/v1/locations", headers=auth_headers(token), json=location_data)


def _create_asset_via_api(client, token, asset_data):
    return client.post("/api/v1/assets", headers=auth_headers(token), json=asset_data)


# =========================================================================
# PERSON / IDENTIFICATION - Reutilización y prevención de duplicados
# =========================================================================

def test_create_customer_creates_new_person_when_identification_not_exists(client, db_session):
    """Al crear un cliente con identificación nueva, se crea Person + identificación + Customer."""
    _, tenant_a, _, token_a, _ = _setup_two_tenants(client, db_session)
    tenant_id = uuid.UUID(tenant_a["id"])

    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Juan Perez",
        "address": "Calle 123",
        "phone": "3511234567",
        "email": "juan@perez.com",
        "notes": "Cliente nuevo",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "12345678", "is_primary": True}
        ],
    }
    response = _create_customer_via_api(client, token_a, payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["display_name"] == "Juan Perez"
    assert data["person_type"] == "INDIVIDUAL"
    assert len(data["identifications"]) == 1
    assert data["identifications"][0]["identification_value"] == "12345678"
    assert data["tenant_id"] == tenant_a["id"]


def test_create_customer_reuses_existing_person_when_identification_exists(client, db_session):
    """Si la identificación ya existe en el tenant PERO la Person no tiene Customer,
    reutiliza la Person y crea Customer (actualizando datos comunes)."""
    _, tenant_a, _, token_a, _ = _setup_two_tenants(client, db_session)

    # Primero crear un TÉCNICO con esa identificación (crea Person + Technician, SIN Customer)
    payload_tech = {
        "person_type": "INDIVIDUAL",
        "display_name": "Carlos Lopez",
        "address": "Calle Falsa 123",
        "phone": "3512222222",
        "email": "carlos@lopez.com",
        "notes": "Técnico de campo",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "87654321", "is_primary": True}
        ],
        "profession": "Técnico en refrigeración",
        "license_number": "MAT-12345",
        "commission_percentage": 10.0,
    }
    resp_t = _create_technician_via_api(client, token_a, payload_tech)
    assert resp_t.status_code == 201
    person_id = resp_t.json()["person_id"]

    # Ahora crear CLIENTE con MISMA identificación - debe reutilizar Person y crear Customer
    payload_cust = {
        "person_type": "INDIVIDUAL",
        "display_name": "Carlos Lopez Cliente",
        "address": "Calle Falsa 123",
        "phone": "3512222222",
        "email": "carlos@lopez.com",
        "notes": "Ahora también es cliente",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "87654321", "is_primary": True}
        ],
    }
    resp_c = _create_customer_via_api(client, token_a, payload_cust)
    assert resp_c.status_code == 201
    data_c = resp_c.json()
    assert data_c["person_id"] == person_id  # MISMA Person
    assert data_c["display_name"] == "Carlos Lopez Cliente"  # Datos actualizados


def test_create_customer_reuses_person_without_customer_specialization(client, db_session):
    """Si la Person existe pero NO tiene Customer, permite crear Customer (reutiliza Person)."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    # Primero crear un TÉCNICO con esa identificación (crea Person + Technician, SIN Customer)
    payload_tech = {
        "person_type": "INDIVIDUAL",
        "display_name": "Carlos Lopez",
        "address": "Calle Falsa 123",
        "phone": "3512222222",
        "email": "carlos@lopez.com",
        "notes": "Técnico de campo",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "87654321", "is_primary": True}
        ],
        "profession": "Técnico en refrigeración",
        "license_number": "MAT-12345",
        "commission_percentage": 10.0,
    }
    resp_t = _create_technician_via_api(client, token_a, payload_tech)
    assert resp_t.status_code == 201
    person_id = resp_t.json()["person_id"]

    # Ahora crear CLIENTE con MISMA identificación - debe reutilizar Person y crear Customer
    payload_cust = {
        "person_type": "INDIVIDUAL",
        "display_name": "Carlos Lopez Cliente",
        "address": "Calle Falsa 123",
        "phone": "3512222222",
        "email": "carlos@lopez.com",
        "notes": "Ahora también es cliente",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "87654321", "is_primary": True}
        ],
    }
    resp_c = _create_customer_via_api(client, token_a, payload_cust)
    assert resp_c.status_code == 201
    data_c = resp_c.json()
    assert data_c["person_id"] == person_id  # MISMA Person
    assert data_c["display_name"] == "Carlos Lopez Cliente"  # Datos actualizados


def test_create_customer_fails_when_person_already_has_customer(client, db_session):
    """Si la Person ya tiene Customer, no permite crear otro (evita duplicados)."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Maria Gomez",
        "address": "Av. Siempre Viva 742",
        "phone": "3511111111",
        "email": "maria@gomez.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "CUIT", "identification_value": "20123456789", "is_primary": True}
        ],
    }
    # Primera creación
    response1 = _create_customer_via_api(client, token_a, payload)
    assert response1.status_code == 201

    # Segunda creación con misma identificación - debe fallar
    response2 = _create_customer_via_api(client, token_a, payload)
    assert response2.status_code == 409
    assert "ya está registrada como Customer" in response2.json()["detail"]


def test_create_technician_reuses_existing_person(client, db_session):
    """Crear técnico reutiliza Person si la identificación ya existe."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    # Primero crear un cliente
    payload_customer = {
        "person_type": "INDIVIDUAL",
        "display_name": "Carlos Lopez",
        "address": "Calle Falsa 123",
        "phone": "3512222222",
        "email": "carlos@lopez.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "87654321", "is_primary": True}
        ],
    }
    resp_c = _create_customer_via_api(client, token_a, payload_customer)
    assert resp_c.status_code == 201
    person_id = resp_c.json()["person_id"]

    # Ahora crear técnico con MISMA identificación - debe reutilizar Person
    payload_tech = {
        "person_type": "INDIVIDUAL",
        "display_name": "Carlos Lopez Tecnico",
        "address": "Calle Falsa 123",
        "phone": "3512222222",
        "email": "carlos@lopez.com",
        "notes": "Técnico de campo",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "87654321", "is_primary": True}
        ],
        "profession": "Técnico en refrigeración",
        "license_number": "MAT-12345",
        "commission_percentage": 10.0,
    }
    resp_t = _create_technician_via_api(client, token_a, payload_tech)
    assert resp_t.status_code == 201
    data_t = resp_t.json()
    assert data_t["person_id"] == person_id  # MISMA Person
    assert data_t["profession"] == "Técnico en refrigeración"
    assert data_t["technician_status"] == "ACTIVE"


def test_create_technician_fails_when_person_already_has_technician(client, db_session):
    """Si la Person ya tiene Technician, no permite crear otro."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Pedro Ruiz",
        "address": "Calle 1",
        "phone": "3513333333",
        "email": "pedro@ruiz.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "11111111", "is_primary": True}
        ],
        "profession": "Electricista",
        "license_number": "ELEC-001",
        "commission_percentage": 5.0,
    }
    # Primera creación
    response1 = _create_technician_via_api(client, token_a, payload)
    assert response1.status_code == 201

    # Segunda creación con misma identificación - debe fallar
    response2 = _create_technician_via_api(client, token_a, payload)
    assert response2.status_code == 409
    assert "ya está registrada como Technician" in response2.json()["detail"]


def test_person_can_be_both_customer_and_technician(client, db_session):
    """Una misma Person puede ser Customer y Technician simultáneamente."""
    _, tenant_a, _, token_a, _ = _setup_two_tenants(client, db_session)

    # Crear cliente
    payload_c = {
        "person_type": "INDIVIDUAL",
        "display_name": "Ana Martinez",
        "address": "Calle 2",
        "phone": "3514444444",
        "email": "ana@martinez.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "22222222", "is_primary": True}
        ],
    }
    resp_c = _create_customer_via_api(client, token_a, payload_c)
    assert resp_c.status_code == 201
    person_id = resp_c.json()["person_id"]

    # Crear técnico con misma identificación
    payload_t = {
        "person_type": "INDIVIDUAL",
        "display_name": "Ana Martinez",
        "address": "Calle 2",
        "phone": "3514444444",
        "email": "ana@martinez.com",
        "notes": "También es técnico",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "22222222", "is_primary": True}
        ],
        "profession": "Técnica en climatización",
        "license_number": "CLIM-001",
        "commission_percentage": 15.0,
    }
    resp_t = _create_technician_via_api(client, token_a, payload_t)
    assert resp_t.status_code == 201
    assert resp_t.json()["person_id"] == person_id

    # Verificar que ambas especializaciones existen consultando ambos endpoints
    customers = client.get("/api/v1/customers", headers=auth_headers(token_a)).json()
    technicians = client.get("/api/v1/technicians", headers=auth_headers(token_a)).json()

    customer_ids = {c["person_id"] for c in customers}
    technician_ids = {t["person_id"] for t in technicians}

    assert person_id in customer_ids
    assert person_id in technician_ids


def test_multiple_identifications_per_person(client, db_session):
    """Una Person puede tener múltiples identificaciones (ej: DNI y CUIT en Argentina)."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    payload = {
        "person_type": "LEGAL",
        "display_name": "Empresa SA",
        "address": "Av. Empresarial 100",
        "phone": "3515555555",
        "email": "contacto@empresa.com",
        "notes": "Persona jurídica",
        "identifications": [
            {"country_code": "AR", "identification_type": "CUIT", "identification_value": "30701234567", "is_primary": True},
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "12345678", "is_primary": False},
        ],
    }
    response = _create_customer_via_api(client, token_a, payload)
    assert response.status_code == 201
    data = response.json()
    assert len(data["identifications"]) == 2
    codes = {i["identification_type"] for i in data["identifications"]}
    assert codes == {"CUIT", "DNI"}


def test_identification_normalization(client, db_session):
    """Los valores de identificación se normalizan (quitan espacios, guiones, mayúsculas)."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    # Crear con formato con guiones y espacios
    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Test Normalizacion",
        "address": "Calle 3",
        "phone": "3516666666",
        "email": "test@norm.com",
        "notes": "",
        "identifications": [
            {"country_code": "ar", "identification_type": "cuit", "identification_value": "20-12345678-9", "is_primary": True}
        ],
    }
    response = _create_customer_via_api(client, token_a, payload)
    assert response.status_code == 201
    data = response.json()
    # Debe guardarse normalizado: sin guiones, mayúsculas
    assert data["identifications"][0]["identification_value"] == "20123456789"
    assert data["identifications"][0]["country_code"] == "AR"
    assert data["identifications"][0]["identification_type"] == "CUIT"


# =========================================================================
# MULTITENANT ISOLATION
# =========================================================================

def test_identification_unique_per_tenant_not_cross_tenant(client, db_session):
    """La misma identificación puede existir en diferentes tenants (unicidad por tenant)."""
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Mismo DNI Distinto Tenant",
        "address": "Calle 4",
        "phone": "3517777777",
        "email": "mismo@dni.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "99999999", "is_primary": True}
        ],
    }

    # Crear en tenant A
    resp_a = _create_customer_via_api(client, token_a, payload)
    assert resp_a.status_code == 201

    # Crear en tenant B con MISMA identificación - DEBE PERMITIRSE
    resp_b = _create_customer_via_api(client, token_b, payload)
    assert resp_b.status_code == 201

    # Deben ser Personas distintas (diferentes person_id)
    assert resp_a.json()["person_id"] != resp_b.json()["person_id"]
    assert resp_a.json()["tenant_id"] == tenant_a["id"]
    assert resp_b.json()["tenant_id"] == tenant_b["id"]


def test_customer_isolation_between_tenants(client, db_session):
    """Los clientes del tenant A no son visibles desde el tenant B."""
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    # Crear cliente en A
    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Cliente Solo En A",
        "address": "Calle A",
        "phone": "3511111111",
        "email": "cliente@a.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "11111111", "is_primary": True}
        ],
    }
    _create_customer_via_api(client, token_a, payload)

    # Listar en A
    customers_a = client.get("/api/v1/customers", headers=auth_headers(token_a)).json()
    # Listar en B
    customers_b = client.get("/api/v1/customers", headers=auth_headers(token_b)).json()

    assert len(customers_a) == 1
    assert customers_a[0]["display_name"] == "Cliente Solo En A"
    assert len(customers_b) == 0


def test_technician_isolation_between_tenants(client, db_session):
    """Los técnicos del tenant A no son visibles desde el tenant B."""
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Tecnico Solo En A",
        "address": "Calle A",
        "phone": "3511111111",
        "email": "tecnico@a.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "22222222", "is_primary": True}
        ],
        "profession": "Técnico A",
        "license_number": "LIC-A",
        "commission_percentage": 10.0,
    }
    _create_technician_via_api(client, token_a, payload)

    techs_a = client.get("/api/v1/technicians", headers=auth_headers(token_a)).json()
    techs_b = client.get("/api/v1/technicians", headers=auth_headers(token_b)).json()

    assert len(techs_a) == 1
    assert len(techs_b) == 0


def test_location_isolation_between_tenants(client, db_session):
    """Las ubicaciones del tenant A no son visibles desde el tenant B."""
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    # Crear cliente en A
    payload_c = {
        "person_type": "INDIVIDUAL",
        "display_name": "Cliente Para Location A",
        "address": "Calle A",
        "phone": "3511111111",
        "email": "cliente@a.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "33333333", "is_primary": True}
        ],
    }
    resp_c = _create_customer_via_api(client, token_a, payload_c)
    customer_id = resp_c.json()["person_id"]

    # Crear location en A
    payload_loc = {"customer_id": customer_id, "name": "Sucursal A", "address": "Calle A 123"}
    _create_location_via_api(client, token_a, payload_loc)

    locs_a = client.get("/api/v1/locations", headers=auth_headers(token_a)).json()
    locs_b = client.get("/api/v1/locations", headers=auth_headers(token_b)).json()

    assert len(locs_a) == 1
    assert len(locs_b) == 0


def test_asset_isolation_between_tenants(client, db_session):
    """Los activos del tenant A no son visibles desde el tenant B."""
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    # Crear cliente en A
    payload_c = {
        "person_type": "INDIVIDUAL",
        "display_name": "Cliente Para Asset A",
        "address": "Calle A",
        "phone": "3511111111",
        "email": "cliente@a.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "44444444", "is_primary": True}
        ],
    }
    resp_c = _create_customer_via_api(client, token_a, payload_c)
    customer_id = resp_c.json()["person_id"]

    # Crear location en A
    payload_loc = {"customer_id": customer_id, "name": "Sucursal Asset A", "address": "Calle A 123"}
    resp_loc = _create_location_via_api(client, token_a, payload_loc)
    location_id = resp_loc.json()["id"]

    # Crear asset en A
    payload_asset = {"location_id": location_id, "name": "Equipo A", "brand": "Marca A"}
    _create_asset_via_api(client, token_a, payload_asset)

    assets_a = client.get("/api/v1/assets", headers=auth_headers(token_a)).json()
    assets_b = client.get("/api/v1/assets", headers=auth_headers(token_b)).json()

    assert len(assets_a) == 1
    assert len(assets_b) == 0


# =========================================================================
# UPDATE PERSON FROM CUSTOMER / TECHNICIAN
# =========================================================================

def test_update_customer_updates_shared_person_data(client, db_session):
    """Actualizar datos desde ficha de Cliente actualiza la Person compartida."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Original Name",
        "address": "Original Address",
        "phone": "3511111111",
        "email": "original@email.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "55555555", "is_primary": True}
        ],
    }
    resp = _create_customer_via_api(client, token_a, payload)
    person_id = resp.json()["person_id"]

    # Actualizar desde cliente
    update_payload = {
        "display_name": "Updated Name",
        "address": "Updated Address",
        "phone": "3519999999",
    }
    update_resp = client.patch(
        f"/api/v1/customers/{person_id}",
        headers=auth_headers(token_a),
        json=update_payload,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["display_name"] == "Updated Name"
    assert data["address"] == "Updated Address"
    assert data["phone"] == "3519999999"


def test_update_technician_updates_shared_person_data(client, db_session):
    """Actualizar datos desde ficha de Técnico actualiza la Person compartida."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": "Tech Original",
        "address": "Tech Address",
        "phone": "3512222222",
        "email": "tech@email.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": "66666666", "is_primary": True}
        ],
        "profession": "Técnico",
        "license_number": "LIC-001",
        "commission_percentage": 10.0,
    }
    resp = _create_technician_via_api(client, token_a, payload)
    person_id = resp.json()["person_id"]

    # Actualizar desde técnico
    update_payload = {
        "display_name": "Tech Updated",
        "address": "Tech Updated Address",
        "profession": "Técnico Senior",
        "technician_status": "INACTIVE",
    }
    update_resp = client.patch(
        f"/api/v1/technicians/{person_id}",
        headers=auth_headers(token_a),
        json=update_payload,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["display_name"] == "Tech Updated"
    assert data["address"] == "Tech Updated Address"
    assert data["profession"] == "Técnico Senior"
    assert data["technician_status"] == "INACTIVE"


# =========================================================================
# LOCATIONS & ASSETS
# =========================================================================

def test_location_belongs_to_customer(client, db_session):
    """Una Location pertenece a un Customer y se filtra por customer_id."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    # Crear dos clientes
    payload_c1 = {
        "person_type": "INDIVIDUAL",
        "display_name": "Cliente 1",
        "address": "Calle 1",
        "phone": "3511111111",
        "email": "c1@test.com",
        "notes": "",
        "identifications": [{"country_code": "AR", "identification_type": "DNI", "identification_value": "77777777", "is_primary": True}],
    }
    payload_c2 = {
        "person_type": "INDIVIDUAL",
        "display_name": "Cliente 2",
        "address": "Calle 2",
        "phone": "3512222222",
        "email": "c2@test.com",
        "notes": "",
        "identifications": [{"country_code": "AR", "identification_type": "DNI", "identification_value": "88888888", "is_primary": True}],
    }
    resp_c1 = _create_customer_via_api(client, token_a, payload_c1)
    resp_c2 = _create_customer_via_api(client, token_a, payload_c2)
    c1_id = resp_c1.json()["person_id"]
    c2_id = resp_c2.json()["person_id"]

    # Crear location para cliente 1
    _create_location_via_api(client, token_a, {"customer_id": c1_id, "name": "Sucursal C1", "address": "Calle C1"})
    # Crear location para cliente 2
    _create_location_via_api(client, token_a, {"customer_id": c2_id, "name": "Sucursal C2", "address": "Calle C2"})

    # Filtrar por cliente 1
    locs_c1 = client.get(f"/api/v1/locations?customer_id={c1_id}", headers=auth_headers(token_a)).json()
    assert len(locs_c1) == 1
    assert locs_c1[0]["name"] == "Sucursal C1"

    # Filtrar por cliente 2
    locs_c2 = client.get(f"/api/v1/locations?customer_id={c2_id}", headers=auth_headers(token_a)).json()
    assert len(locs_c2) == 1
    assert locs_c2[0]["name"] == "Sucursal C2"


def test_asset_belongs_to_location(client, db_session):
    """Un Asset pertenece a una Location y se filtra por location_id."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    # Crear cliente
    payload_c = {
        "person_type": "INDIVIDUAL",
        "display_name": "Cliente Assets",
        "address": "Calle",
        "phone": "3513333333",
        "email": "c@test.com",
        "notes": "",
        "identifications": [{"country_code": "AR", "identification_type": "DNI", "identification_value": "99999998", "is_primary": True}],
    }
    resp_c = _create_customer_via_api(client, token_a, payload_c)
    c_id = resp_c.json()["person_id"]

    # Crear dos ubicaciones
    resp_l1 = _create_location_via_api(client, token_a, {"customer_id": c_id, "name": "Ubicacion 1"})
    resp_l2 = _create_location_via_api(client, token_a, {"customer_id": c_id, "name": "Ubicacion 2"})
    l1_id = resp_l1.json()["id"]
    l2_id = resp_l2.json()["id"]

    # Crear asset en ubicación 1
    _create_asset_via_api(client, token_a, {"location_id": l1_id, "name": "Equipo Loc 1"})
    # Crear asset en ubicación 2
    _create_asset_via_api(client, token_a, {"location_id": l2_id, "name": "Equipo Loc 2"})

    # Filtrar por ubicación 1
    assets_l1 = client.get(f"/api/v1/assets?location_id={l1_id}", headers=auth_headers(token_a)).json()
    assert len(assets_l1) == 1
    assert assets_l1[0]["name"] == "Equipo Loc 1"

    # Filtrar por ubicación 2
    assets_l2 = client.get(f"/api/v1/assets?location_id={l2_id}", headers=auth_headers(token_a)).json()
    assert len(assets_l2) == 1
    assert assets_l2[0]["name"] == "Equipo Loc 2"


def test_asset_type_filter(client, db_session):
    """Filtrar activos por tipo de activo."""
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    # Obtener un asset_type existente del tenant
    asset_types = client.get("/api/v1/asset-types", headers=auth_headers(token_a)).json()
    at_id = asset_types[0]["id"]

    # Crear cliente y ubicación
    payload_c = {
        "person_type": "INDIVIDUAL",
        "display_name": "Cliente Filter",
        "address": "Calle",
        "phone": "3514444444",
        "email": "cf@test.com",
        "notes": "",
        "identifications": [{"country_code": "AR", "identification_type": "DNI", "identification_value": "99999997", "is_primary": True}],
    }
    resp_c = _create_customer_via_api(client, token_a, payload_c)
    c_id = resp_c.json()["person_id"]

    resp_l = _create_location_via_api(client, token_a, {"customer_id": c_id, "name": "Ubicacion Filter"})
    l_id = resp_l.json()["id"]

    # Crear asset con asset_type
    _create_asset_via_api(client, token_a, {"location_id": l_id, "name": "Equipo Con Tipo", "asset_type_id": at_id})
    # Crear asset sin asset_type
    _create_asset_via_api(client, token_a, {"location_id": l_id, "name": "Equipo Sin Tipo"})

    # Filtrar por asset_type
    assets_with_type = client.get(f"/api/v1/assets?asset_type_id={at_id}", headers=auth_headers(token_a)).json()
    assert len(assets_with_type) == 1
    assert assets_with_type[0]["name"] == "Equipo Con Tipo"
    assert assets_with_type[0]["asset_type"]["id"] == at_id


# =========================================================================
# SERVICE LAYER UNIT TESTS
# =========================================================================

def test_person_service_find_by_identification(db_session):
    """PersonService.find_person_by_identification encuentra persona por identificación."""
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.role import Role, TENANT_ADMIN
    from app.core.security import hash_password

    # Setup tenant y usuario
    tenant = Tenant(name="Test Tenant", commercial_name="Test")
    db_session.add(tenant)
    db_session.flush()

    admin_role = db_session.scalar(select(Role).where(Role.code == TENANT_ADMIN))
    user = User(tenant_id=tenant.id, role_id=admin_role.id, email="test@test.com", full_name="Test", password_hash=hash_password("pass"))
    db_session.add(user)
    db_session.commit()

    service = PersonService(db_session)

    # Crear persona con identificación
    person = service.create_person_with_identification(
        tenant_id=tenant.id,
        person_type=PersonType.INDIVIDUAL,
        display_name="Test Person",
        address="Addr",
        phone="123",
        email="test@person.com",
        notes="",
        identifications=[
            PersonIdentification(
                tenant_id=tenant.id,
                person_id=uuid.uuid4(),
                country_code="AR",
                identification_type="DNI",
                identification_value="12345678",
                is_primary=True,
            )
        ],
        created_by=user.id,
    )
    db_session.commit()

    # Buscar por identificación
    found = service.find_person_by_identification(tenant.id, "AR", "DNI", "12345678")
    assert found is not None
    assert found.id == person.id

    # Buscar con formato diferente (normalización)
    found2 = service.find_person_by_identification(tenant.id, "ar", "dni", "12.345.678")
    assert found2 is not None
    assert found2.id == person.id

    # No encontrado
    not_found = service.find_person_by_identification(tenant.id, "AR", "DNI", "99999999")
    assert not_found is None


def test_person_service_specialization_already_exists(db_session):
    """PersonService lanza SpecializationAlreadyExists si ya existe la especialización."""
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.role import Role, TENANT_ADMIN
    from app.core.security import hash_password

    tenant = Tenant(name="Test Tenant 2", commercial_name="Test 2")
    db_session.add(tenant)
    db_session.flush()

    admin_role = db_session.scalar(select(Role).where(Role.code == TENANT_ADMIN))
    user = User(tenant_id=tenant.id, role_id=admin_role.id, email="test2@test.com", full_name="Test 2", password_hash=hash_password("pass"))
    db_session.add(user)
    db_session.commit()

    service = PersonService(db_session)

    person = service.create_person_with_identification(
        tenant_id=tenant.id,
        person_type=PersonType.INDIVIDUAL,
        display_name="Test Person 2",
        address="Addr",
        phone="123",
        email="test2@person.com",
        notes="",
        identifications=[
            PersonIdentification(
                tenant_id=tenant.id,
                person_id=uuid.uuid4(),
                country_code="AR",
                identification_type="DNI",
                identification_value="11111111",
                is_primary=True,
            )
        ],
        created_by=user.id,
    )
    db_session.flush()

    # Crear Customer
    service.create_customer(tenant.id, person, user.id)
    db_session.flush()

    # Intentar crear Customer de nuevo -> error
    try:
        service.create_customer(tenant.id, person, user.id)
        assert False, "Debería haber lanzado SpecializationAlreadyExists"
    except SpecializationAlreadyExists as e:
        assert e.specialization == "Customer"

    # Intentar crear Technician -> OK (distinta especialización)
    tech = service.create_technician(tenant.id, person, "Prof", "LIC", 10.0, user.id)
    assert tech is not None

    # Intentar crear Technician de nuevo -> error
    try:
        service.create_technician(tenant.id, person, "Prof", "LIC", 10.0, user.id)
        assert False, "Debería haber lanzado SpecializationAlreadyExists"
    except SpecializationAlreadyExists as e:
        assert e.specialization == "Technician"