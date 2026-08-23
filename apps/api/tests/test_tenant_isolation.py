"""Prueba de aislamiento multitenant (docs/tecnica/arquitectura.md §3.5).

Un usuario del Tenant A nunca debe poder leer ni modificar datos del
Tenant B, y el tenant de contexto siempre se resuelve server-side —
nunca a partir de un valor enviado por el cliente.
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


def test_tenant_admin_only_sees_own_tenant_users(client, db_session):
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    client.post(
        "/api/v1/users",
        headers=auth_headers(token_a),
        json={
            "email": "tecnico@stc.com.ar",
            "full_name": "Juan Perez",
            "password": "Tecni123!",
            "role_code": "TENANT_TECHNICIAN",
        },
    )

    users_a = client.get("/api/v1/users", headers=auth_headers(token_a)).json()
    users_b = client.get("/api/v1/users", headers=auth_headers(token_b)).json()

    emails_a = {u["email"] for u in users_a}
    emails_b = {u["email"] for u in users_b}

    assert emails_a == {"admin@stc.com.ar", "tecnico@stc.com.ar"}
    assert emails_b == {"admin@adl.com.ar"}
    # Ningún usuario de A es visible desde B ni viceversa.
    assert emails_a.isdisjoint(emails_b)


def test_tenant_config_is_isolated_between_tenants(client, db_session):
    _, tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    client.patch(
        "/api/v1/tenant-config",
        headers=auth_headers(token_a),
        json={"commercial_display_name": "Nombre secreto de A"},
    )

    config_a = client.get("/api/v1/tenant-config", headers=auth_headers(token_a)).json()
    config_b = client.get("/api/v1/tenant-config", headers=auth_headers(token_b)).json()

    assert config_a["tenant_id"] == tenant_a["id"]
    assert config_b["tenant_id"] == tenant_b["id"]
    assert config_a["commercial_display_name"] == "Nombre secreto de A"
    assert config_b["commercial_display_name"] != "Nombre secreto de A"


def test_client_supplied_tenant_id_is_ignored(client, db_session):
    """Ningún endpoint acepta tenant_id del cliente: el resuelto server-side
    (a partir del token) es el único que importa, aunque se intente inyectar
    otro por query string.
    """
    _, tenant_a, tenant_b, token_a, _ = _setup_two_tenants(client, db_session)

    response = client.get(
        f"/api/v1/tenant-config?tenant_id={tenant_b['id']}",
        headers=auth_headers(token_a),
    )

    assert response.status_code == 200
    assert response.json()["tenant_id"] == tenant_a["id"]


def test_non_platform_owner_cannot_manage_tenants(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    assert client.get("/api/v1/tenants", headers=auth_headers(token_a)).status_code == 403
    assert (
        client.post(
            "/api/v1/tenants",
            headers=auth_headers(token_a),
            json={
                "name": "Intento no autorizado",
                "admin_email": "hack@x.com",
                "admin_full_name": "Hacker",
                "admin_password": "x",
            },
        ).status_code
        == 403
    )


def test_technician_cannot_list_users_or_edit_config(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)

    client.post(
        "/api/v1/users",
        headers=auth_headers(token_a),
        json={
            "email": "tecnico@stc.com.ar",
            "full_name": "Juan Perez",
            "password": "Tecni123!",
            "role_code": "TENANT_TECHNICIAN",
        },
    )
    token_tech = login(client, "tecnico@stc.com.ar", "Tecni123!")

    assert client.get("/api/v1/users", headers=auth_headers(token_tech)).status_code == 403
    assert (
        client.patch(
            "/api/v1/tenant-config",
            headers=auth_headers(token_tech),
            json={"commercial_display_name": "no debería poder"},
        ).status_code
        == 403
    )


def test_platform_owner_endpoints_require_authentication(client):
    assert client.get("/api/v1/tenants").status_code == 401
    assert client.get("/api/v1/users").status_code == 401
    assert client.get("/api/v1/tenant-config").status_code == 401
