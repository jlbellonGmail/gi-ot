"""Pruebas de la Etapa 04/05 — Núcleo de Órdenes de Trabajo y MVP vertical
(ROADMAP.md §04, §05).

Cubren la máquina de estados completa de la OT, historial de auditoría,
y el aislamiento multitenant en operaciones de OT.
"""

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


def _create_customer(client, token, suffix="1"):
    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": f"Cliente {suffix}",
        "address": "Calle Falsa 123",
        "phone": "3511111111",
        "email": f"cliente{suffix}@x.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": f"1000000{suffix}", "is_primary": True}
        ],
    }
    resp = client.post("/api/v1/customers", headers=auth_headers(token), json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["person_id"]


def _create_technician(client, token, suffix="1"):
    payload = {
        "person_type": "INDIVIDUAL",
        "display_name": f"Tecnico {suffix}",
        "address": "Calle Falsa 456",
        "phone": "3512222222",
        "email": f"tecnico{suffix}@x.com",
        "notes": "",
        "identifications": [
            {"country_code": "AR", "identification_type": "DNI", "identification_value": f"2000000{suffix}", "is_primary": True}
        ],
        "profession": "Electricista",
        "license_number": f"LIC-{suffix}",
        "commission_percentage": 10.0,
    }
    resp = client.post("/api/v1/technicians", headers=auth_headers(token), json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["person_id"]


def _create_location(client, token, customer_id, suffix="1"):
    payload = {"customer_id": customer_id, "name": f"Sucursal {suffix}", "address": "Calle A 123"}
    resp = client.post("/api/v1/locations", headers=auth_headers(token), json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_asset(client, token, location_id, suffix="1"):
    payload = {"location_id": location_id, "name": f"Equipo {suffix}", "brand": "Marca X"}
    resp = client.post("/api/v1/assets", headers=auth_headers(token), json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _first_id(client, token, path):
    resp = client.get(path, headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    items = resp.json()
    assert items, f"{path} no devolvió elementos"
    return items[0]["id"]


def _create_technician_user(client, token, email="tecnico@stc.com.ar", password="Tecni123!"):
    resp = client.post(
        "/api/v1/users",
        headers=auth_headers(token),
        json={"email": email, "full_name": "Juan Perez", "password": password, "role_code": "TENANT_TECHNICIAN"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _full_wo_setup(client, token, suffix="1"):
    """Crea cliente → ubicación → activo y devuelve refs listas para crear una OT."""
    customer_id = _create_customer(client, token, suffix)
    location_id = _create_location(client, token, customer_id, suffix)
    asset_id = _create_asset(client, token, location_id, suffix)
    work_order_type_id = _first_id(client, token, "/api/v1/work-order-types")
    priority_id = _first_id(client, token, "/api/v1/priorities")
    return {
        "customer_id": customer_id,
        "location_id": location_id,
        "asset_id": asset_id,
        "work_order_type_id": work_order_type_id,
        "priority_id": priority_id,
        "requested_description": "El equipo no enciende",
    }


# =========================================================================
# CICLO DE VIDA DE LA OT
# =========================================================================

def test_create_wo_starts_as_pending_with_created_history(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    payload = _full_wo_setup(client, token_a)

    resp = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload)
    assert resp.status_code == 201, resp.text
    wo = resp.json()
    assert wo["status_code"] == "PENDING"
    assert wo["number"] == 1
    assert wo["is_terminal"] is False

    history = client.get(f"/api/v1/work-orders/{wo['id']}/history", headers=auth_headers(token_a)).json()
    assert len(history) == 1
    assert history[0]["event_type"] == "CREATED"


def test_wo_numbers_are_sequential_per_tenant(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    payload1 = _full_wo_setup(client, token_a, "1")
    payload2 = _full_wo_setup(client, token_a, "2")

    wo1 = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload1).json()
    wo2 = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload2).json()

    assert wo1["number"] == 1
    assert wo2["number"] == 2


def test_office_creates_and_assigns_technician_then_technician_executes_and_closes(client, db_session):
    """Circuito completo (ROADMAP §05): Tenant → Usuario → Cliente → Ubicación →
    Activo → OT → Técnico → Ejecución → Cierre → Historial."""
    _, _, _, token_admin, _ = _setup_two_tenants(client, db_session)

    technician_person_id = _create_technician(client, token_admin)
    _create_technician_user(client, token_admin)
    token_tech = login(client, "tecnico@stc.com.ar", "Tecni123!")

    payload = _full_wo_setup(client, token_admin)
    wo = client.post("/api/v1/work-orders", headers=auth_headers(token_admin), json=payload).json()
    wo_id = wo["id"]

    # Oficina/Admin asigna técnico
    resp = client.post(
        f"/api/v1/work-orders/{wo_id}/assign",
        headers=auth_headers(token_admin),
        json={"technician_id": technician_person_id},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["technician_id"] == technician_person_id

    # Técnico inicia la OT
    resp = client.post(f"/api/v1/work-orders/{wo_id}/start", headers=auth_headers(token_tech))
    assert resp.status_code == 200, resp.text
    assert resp.json()["status_code"] == "IN_PROGRESS"
    assert resp.json()["started_at"] is not None

    # Técnico registra el trabajo realizado
    resp = client.post(
        f"/api/v1/work-orders/{wo_id}/register-work",
        headers=auth_headers(token_tech),
        json={"performed_description": "Se reemplazó el fusible"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["performed_description"] == "Se reemplazó el fusible"

    # Técnico cierra la OT
    resp = client.post(
        f"/api/v1/work-orders/{wo_id}/finish",
        headers=auth_headers(token_tech),
        json={"status_code": "COMPLETED"},
    )
    assert resp.status_code == 200, resp.text
    finished = resp.json()
    assert finished["status_code"] == "COMPLETED"
    assert finished["is_terminal"] is True
    assert finished["finished_at"] is not None

    # Oficina consulta el resultado
    resp = client.get(f"/api/v1/work-orders/{wo_id}", headers=auth_headers(token_admin))
    assert resp.status_code == 200
    assert resp.json()["status_code"] == "COMPLETED"

    # El historial refleja todos los eventos en orden
    history = client.get(f"/api/v1/work-orders/{wo_id}/history", headers=auth_headers(token_admin)).json()
    event_types = [h["event_type"] for h in history]
    assert event_types.count("CREATED") == 1
    assert event_types.count("ASSIGNED") == 1
    assert event_types.count("STATUS_CHANGE") == 2  # start (IN_PROGRESS) + finish (COMPLETED)

    # El activo conserva historial: se puede filtrar por cliente y sigue accesible
    wos_of_customer = client.get(
        f"/api/v1/work-orders?customer_id={payload['customer_id']}", headers=auth_headers(token_admin)
    ).json()
    assert any(w["id"] == wo_id for w in wos_of_customer)


def test_invalid_transition_is_rejected(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    payload = _full_wo_setup(client, token_a)
    wo = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload).json()

    # No se puede finalizar sin haber iniciado
    resp = client.post(
        f"/api/v1/work-orders/{wo['id']}/finish",
        headers=auth_headers(token_a),
        json={"status_code": "COMPLETED"},
    )
    assert resp.status_code == 409


def test_cannot_update_terminal_wo_without_reopening(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    payload = _full_wo_setup(client, token_a)
    wo = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload).json()

    client.post(f"/api/v1/work-orders/{wo['id']}/start", headers=auth_headers(token_a))
    client.post(
        f"/api/v1/work-orders/{wo['id']}/finish",
        headers=auth_headers(token_a),
        json={"status_code": "UNRESOLVED"},
    )

    resp = client.patch(
        f"/api/v1/work-orders/{wo['id']}",
        headers=auth_headers(token_a),
        json={"requested_description": "nuevo texto"},
    )
    assert resp.status_code == 409


def test_reopen_controlled_requires_notes_and_only_office_admin(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    _create_technician_user(client, token_a)
    token_tech = login(client, "tecnico@stc.com.ar", "Tecni123!")

    payload = _full_wo_setup(client, token_a)
    wo = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload).json()
    client.post(f"/api/v1/work-orders/{wo['id']}/start", headers=auth_headers(token_a))
    client.post(
        f"/api/v1/work-orders/{wo['id']}/finish",
        headers=auth_headers(token_a),
        json={"status_code": "UNRESOLVED"},
    )

    # El técnico no puede reabrir
    resp = client.post(
        f"/api/v1/work-orders/{wo['id']}/reopen",
        headers=auth_headers(token_tech),
        json={"notes": "reintentar"},
    )
    assert resp.status_code == 403

    # notes es obligatorio (min_length=3)
    resp = client.post(
        f"/api/v1/work-orders/{wo['id']}/reopen", headers=auth_headers(token_a), json={"notes": ""}
    )
    assert resp.status_code == 422

    # Oficina/Admin reabre con motivo
    resp = client.post(
        f"/api/v1/work-orders/{wo['id']}/reopen",
        headers=auth_headers(token_a),
        json={"notes": "Cliente reportó que sigue fallando"},
    )
    assert resp.status_code == 200, resp.text
    reopened = resp.json()
    assert reopened["status_code"] == "PENDING"
    assert reopened["started_at"] is None
    assert reopened["finished_at"] is None

    history = client.get(f"/api/v1/work-orders/{wo['id']}/history", headers=auth_headers(token_a)).json()
    assert any(h["event_type"] == "REOPENED" and h["notes"] for h in history)


def test_only_office_admin_can_create_wo(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    _create_technician_user(client, token_a)
    token_tech = login(client, "tecnico@stc.com.ar", "Tecni123!")

    payload = _full_wo_setup(client, token_a)
    resp = client.post("/api/v1/work-orders", headers=auth_headers(token_tech), json=payload)
    assert resp.status_code == 403


# =========================================================================
# AISLAMIENTO MULTITENANT
# =========================================================================

def test_wo_isolation_between_tenants(client, db_session):
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    payload_a = _full_wo_setup(client, token_a, "a")
    client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload_a)

    wos_a = client.get("/api/v1/work-orders", headers=auth_headers(token_a)).json()
    wos_b = client.get("/api/v1/work-orders", headers=auth_headers(token_b)).json()

    assert len(wos_a) == 1
    assert len(wos_b) == 0


def test_tenant_b_cannot_read_or_operate_on_tenant_a_wo(client, db_session):
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    payload_a = _full_wo_setup(client, token_a, "a")
    wo_a = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload_a).json()

    assert client.get(f"/api/v1/work-orders/{wo_a['id']}", headers=auth_headers(token_b)).status_code == 404
    assert (
        client.post(f"/api/v1/work-orders/{wo_a['id']}/start", headers=auth_headers(token_b)).status_code
        == 404
    )
    assert (
        client.get(f"/api/v1/work-orders/{wo_a['id']}/history", headers=auth_headers(token_b)).status_code
        == 404
    )


def test_cannot_create_wo_referencing_another_tenants_customer(client, db_session):
    """Un tenant no puede crear una OT usando refs (cliente/ubicación/activo)
    que pertenecen a otro tenant, aunque conozca sus IDs."""
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    payload_a = _full_wo_setup(client, token_a, "a")

    # token_b intenta crear una OT usando las refs del tenant A
    cross_payload = dict(payload_a)
    resp = client.post("/api/v1/work-orders", headers=auth_headers(token_b), json=cross_payload)
    assert resp.status_code == 400


def test_cannot_assign_technician_from_another_tenant(client, db_session):
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    tech_b_id = _create_technician(client, token_b, "b")

    payload_a = _full_wo_setup(client, token_a, "a")
    wo_a = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload_a).json()

    resp = client.post(
        f"/api/v1/work-orders/{wo_a['id']}/assign",
        headers=auth_headers(token_a),
        json={"technician_id": tech_b_id},
    )
    assert resp.status_code == 404
