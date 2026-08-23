"""Pruebas de lectura de activo por código QR (ROADMAP.md §06 — Lectura QR)."""

from tests.helpers import auth_headers, create_platform_owner, create_tenant_via_api, login
from tests.test_work_orders import _create_asset, _create_customer, _create_location


def _setup_tenant(client, db_session, admin_email="admin@stc.com.ar"):
    create_platform_owner(db_session)
    owner_token = login(client, "owner@gi-ot.com", "Owner123!")
    create_tenant_via_api(client, owner_token, "Servicio Tecnico Cordoba", admin_email, "AdminA123!")
    return owner_token, login(client, admin_email, "AdminA123!")


def _create_asset_with_qr(client, token, qr_code, suffix="1"):
    customer_id = _create_customer(client, token, suffix)
    location_id = _create_location(client, token, customer_id, suffix)
    resp = client.post(
        "/api/v1/assets",
        headers=auth_headers(token),
        json={"location_id": location_id, "name": f"Equipo {suffix}", "brand": "Marca X", "qr_code": qr_code},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_lookup_asset_by_qr_code(client, db_session):
    _, token = _setup_tenant(client, db_session)
    asset = _create_asset_with_qr(client, token, "QR-ABC-123")

    resp = client.get("/api/v1/assets/qr/QR-ABC-123", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == asset["id"]


def test_lookup_unknown_qr_code_is_404(client, db_session):
    _, token = _setup_tenant(client, db_session)
    resp = client.get("/api/v1/assets/qr/NO-EXISTE", headers=auth_headers(token))
    assert resp.status_code == 404


def test_qr_lookup_isolated_between_tenants(client, db_session):
    owner_token, token_a = _setup_tenant(client, db_session, "admin@stc.com.ar")
    create_tenant_via_api(client, owner_token, "Ascensores del Litoral", "admin@adl.com.ar", "AdminB123!")
    token_b = login(client, "admin@adl.com.ar", "AdminB123!")

    _create_asset_with_qr(client, token_a, "QR-SHARED-1")

    resp = client.get("/api/v1/assets/qr/QR-SHARED-1", headers=auth_headers(token_b))
    assert resp.status_code == 404
