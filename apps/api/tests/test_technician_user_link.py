"""Pruebas de vínculo Técnico ↔ Usuario y OT urgente por técnico
(ROADMAP.md §06 — Mobile / PWA)."""

from tests.helpers import auth_headers, create_platform_owner, create_tenant_via_api, login
from tests.test_work_orders import _create_technician, _create_technician_user, _full_wo_setup


def _setup_tenant(client, db_session, admin_email="admin@stc.com.ar"):
    create_platform_owner(db_session)
    owner_token = login(client, "owner@gi-ot.com", "Owner123!")
    create_tenant_via_api(client, owner_token, "Servicio Tecnico Cordoba", admin_email, "AdminA123!")
    return owner_token, login(client, admin_email, "AdminA123!")


def test_link_and_unlink_technician_user(client, db_session):
    _, token = _setup_tenant(client, db_session)
    person_id = _create_technician(client, token)
    user = _create_technician_user(client, token)

    resp = client.patch(
        f"/api/v1/technicians/{person_id}/user", headers=auth_headers(token), json={"user_id": user["id"]}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["user_id"] == user["id"]

    resp = client.patch(
        f"/api/v1/technicians/{person_id}/user", headers=auth_headers(token), json={"user_id": None}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["user_id"] is None


def test_cannot_link_user_with_wrong_role(client, db_session):
    _, token = _setup_tenant(client, db_session)
    person_id = _create_technician(client, token)
    resp = client.post(
        "/api/v1/users",
        headers=auth_headers(token),
        json={"email": "office@stc.com.ar", "full_name": "Ana Office", "password": "Office123!", "role_code": "TENANT_OFFICE"},
    )
    assert resp.status_code == 201, resp.text
    office_user = resp.json()

    resp = client.patch(
        f"/api/v1/technicians/{person_id}/user",
        headers=auth_headers(token),
        json={"user_id": office_user["id"]},
    )
    assert resp.status_code == 400


def test_cannot_link_same_user_to_two_technicians(client, db_session):
    _, token = _setup_tenant(client, db_session)
    person_id_1 = _create_technician(client, token, "1")
    person_id_2 = _create_technician(client, token, "2")
    user = _create_technician_user(client, token)

    resp = client.patch(
        f"/api/v1/technicians/{person_id_1}/user", headers=auth_headers(token), json={"user_id": user["id"]}
    )
    assert resp.status_code == 200, resp.text

    resp = client.patch(
        f"/api/v1/technicians/{person_id_2}/user", headers=auth_headers(token), json={"user_id": user["id"]}
    )
    assert resp.status_code == 400


def test_cannot_link_user_from_another_tenant(client, db_session):
    owner_token, token_a = _setup_tenant(client, db_session, "admin@stc.com.ar")
    create_tenant_via_api(client, owner_token, "Ascensores del Litoral", "admin@adl.com.ar", "AdminB123!")
    token_b = login(client, "admin@adl.com.ar", "AdminB123!")

    person_id_a = _create_technician(client, token_a)
    user_b = _create_technician_user(client, token_b, email="tecnico@adl.com.ar")

    resp = client.patch(
        f"/api/v1/technicians/{person_id_a}/user", headers=auth_headers(token_a), json={"user_id": user_b["id"]}
    )
    assert resp.status_code == 400


def test_technician_only_role_cannot_link(client, db_session):
    _, token = _setup_tenant(client, db_session)
    person_id = _create_technician(client, token)
    user = _create_technician_user(client, token)
    token_tech = login(client, "tecnico@stc.com.ar", "Tecni123!")

    resp = client.patch(
        f"/api/v1/technicians/{person_id}/user", headers=auth_headers(token_tech), json={"user_id": user["id"]}
    )
    assert resp.status_code == 403


# =========================================================================
# OT urgente (técnico, desde campo)
# =========================================================================

def test_linked_technician_creates_urgent_wo_self_assigned(client, db_session):
    _, token = _setup_tenant(client, db_session)
    person_id = _create_technician(client, token)
    user = _create_technician_user(client, token)
    link_resp = client.patch(
        f"/api/v1/technicians/{person_id}/user",
        headers=auth_headers(token),
        json={"user_id": user["id"]},
    )
    assert link_resp.status_code == 200, link_resp.text
    token_tech = login(client, "tecnico@stc.com.ar", "Tecni123!")

    payload = _full_wo_setup(client, token)
    resp = client.post("/api/v1/work-orders", headers=auth_headers(token_tech), json=payload)
    assert resp.status_code == 201, resp.text
    wo = resp.json()
    assert wo["priority_code"] == "URGENT"
    assert wo["technician_id"] == person_id


def test_unlinked_technician_cannot_create_wo(client, db_session):
    _, token = _setup_tenant(client, db_session)
    _create_technician_user(client, token)
    token_tech = login(client, "tecnico@stc.com.ar", "Tecni123!")

    payload = _full_wo_setup(client, token)
    resp = client.post("/api/v1/work-orders", headers=auth_headers(token_tech), json=payload)
    assert resp.status_code == 403


def test_office_admin_creates_wo_priority_unaffected(client, db_session):
    _, token = _setup_tenant(client, db_session)
    payload = _full_wo_setup(client, token)
    resp = client.post("/api/v1/work-orders", headers=auth_headers(token), json=payload)
    assert resp.status_code == 201, resp.text
    assert resp.json()["priority_code"] != "URGENT"
