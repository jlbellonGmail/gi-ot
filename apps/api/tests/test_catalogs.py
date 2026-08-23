"""Pruebas de la Etapa 02 — Parametrización (ROADMAP.md §02).

Cubren: siembra por defecto al crear un tenant, idempotencia de esa
siembra, aislamiento multitenant, unicidad de `code` por tenant, permisos
por rol, y la semántica interna fija de `WorkOrderStatus.code`.
"""

import uuid

from sqlalchemy import select

from app.core.provisioning import provision_tenant_from_template
from app.models.asset_type import AssetType
from app.models.priority import Priority
from app.models.work_order_status import WorkOrderStatus
from app.models.work_order_type import WorkOrderType
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

    return tenant_a, tenant_b, token_a, token_b


def _create_technician(client, admin_token, email="tecnico@stc.com.ar", password="Tecni123!"):
    client.post(
        "/api/v1/users",
        headers=auth_headers(admin_token),
        json={
            "email": email,
            "full_name": "Juan Perez",
            "password": password,
            "role_code": "TENANT_TECHNICIAN",
        },
    )
    return login(client, email, password)


# ---------------------------------------------------------------------------
# Siembra por defecto
# ---------------------------------------------------------------------------


def test_new_tenant_is_seeded_with_default_priorities_types_statuses_and_asset_types(client, db_session):
    tenant_a, _, token_a, _ = _setup_two_tenants(client, db_session)

    priorities = client.get("/api/v1/priorities", headers=auth_headers(token_a)).json()
    work_order_types = client.get("/api/v1/work-order-types", headers=auth_headers(token_a)).json()
    statuses = client.get("/api/v1/work-order-statuses", headers=auth_headers(token_a)).json()
    asset_types = client.get("/api/v1/asset-types", headers=auth_headers(token_a)).json()

    assert {p["code"] for p in priorities} == {"LOW", "NORMAL", "HIGH", "URGENT"}
    assert all(p["tenant_id"] == tenant_a["id"] for p in priorities)

    assert {t["code"] for t in work_order_types} == {
        "CORRECTIVE",
        "PREVENTIVE",
        "INSTALLATION",
        "REVIEW",
        "INSPECTION",
        "WARRANTY",
    }

    assert {s["code"] for s in statuses} == {"PENDING", "IN_PROGRESS", "COMPLETED", "UNRESOLVED"}
    terminal_codes = {s["code"] for s in statuses if s["is_terminal"]}
    assert terminal_codes == {"COMPLETED", "UNRESOLVED"}

    assert {a["code"] for a in asset_types} == {"EQUIPMENT", "INSTALLATION", "OTHER"}
    assert all(a["tenant_id"] == tenant_a["id"] for a in asset_types)


def test_two_tenants_receive_independent_seed_rows(client, db_session):
    """Cada tenant recibe su propia copia de los valores iniciales: son
    filas distintas, no una referencia compartida (modelo-datos.md §5)."""
    tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    priorities_a = client.get("/api/v1/priorities", headers=auth_headers(token_a)).json()
    priorities_b = client.get("/api/v1/priorities", headers=auth_headers(token_b)).json()

    ids_a = {p["id"] for p in priorities_a}
    ids_b = {p["id"] for p in priorities_b}

    assert ids_a.isdisjoint(ids_b)
    assert {p["code"] for p in priorities_a} == {p["code"] for p in priorities_b}


def test_modifying_tenant_a_seed_does_not_affect_tenant_b(client, db_session):
    _, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    statuses_a = client.get("/api/v1/work-order-statuses", headers=auth_headers(token_a)).json()
    pending_a = next(s for s in statuses_a if s["code"] == "PENDING")

    client.patch(
        f"/api/v1/work-order-statuses/{pending_a['id']}",
        headers=auth_headers(token_a),
        json={"label": "En cola de A"},
    )

    statuses_b = client.get("/api/v1/work-order-statuses", headers=auth_headers(token_b)).json()
    pending_b = next(s for s in statuses_b if s["code"] == "PENDING")

    assert pending_b["label"] == "Pendiente"
    assert pending_b["tenant_id"] == tenant_b["id"]


def test_running_seed_again_does_not_duplicate_records(client, db_session):
    """La siembra es idempotente: reejecutarla sobre un tenant ya
    inicializado no debe duplicar filas (ROADMAP.md §02)."""
    tenant_a, _, _, _ = _setup_two_tenants(client, db_session)
    tenant_id = uuid.UUID(tenant_a["id"])

    def _counts():
        return {
            "priorities": len(db_session.scalars(select(Priority).where(Priority.tenant_id == tenant_id)).all()),
            "work_order_types": len(
                db_session.scalars(select(WorkOrderType).where(WorkOrderType.tenant_id == tenant_id)).all()
            ),
            "work_order_statuses": len(
                db_session.scalars(select(WorkOrderStatus).where(WorkOrderStatus.tenant_id == tenant_id)).all()
            ),
            "asset_types": len(
                db_session.scalars(select(AssetType).where(AssetType.tenant_id == tenant_id)).all()
            ),
        }

    before = _counts()

    provision_tenant_from_template(db_session, tenant_id)
    provision_tenant_from_template(db_session, tenant_id)
    db_session.commit()

    after = _counts()

    assert before == after
    assert after == {
        "priorities": 4,
        "work_order_types": 6,
        "work_order_statuses": 4,
        "asset_types": 3,
    }


# ---------------------------------------------------------------------------
# Aislamiento multitenant
# ---------------------------------------------------------------------------


def test_asset_types_are_isolated_between_tenants(client, db_session):
    tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    client.post(
        "/api/v1/asset-types",
        headers=auth_headers(token_a),
        json={"code": "SPLIT", "label": "Split"},
    )

    asset_types_a = client.get("/api/v1/asset-types", headers=auth_headers(token_a)).json()
    asset_types_b = client.get("/api/v1/asset-types", headers=auth_headers(token_b)).json()

    assert "SPLIT" in {a["code"] for a in asset_types_a}
    assert "SPLIT" not in {a["code"] for a in asset_types_b}
    assert all(a["tenant_id"] == tenant_a["id"] for a in asset_types_a)


def test_tenant_cannot_update_another_tenants_priority(client, db_session):
    _, _, token_a, token_b = _setup_two_tenants(client, db_session)

    priorities_b = client.get("/api/v1/priorities", headers=auth_headers(token_b)).json()
    priority_b_id = next(p["id"] for p in priorities_b if p["code"] == "URGENT")

    response = client.patch(
        f"/api/v1/priorities/{priority_b_id}",
        headers=auth_headers(token_a),
        json={"label": "Robado"},
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Creación, modificación y unicidad
# ---------------------------------------------------------------------------


def test_admin_can_create_and_rename_work_order_type(client, db_session):
    _, _, token_a, _ = _setup_two_tenants(client, db_session)

    create_response = client.post(
        "/api/v1/work-order-types",
        headers=auth_headers(token_a),
        json={"code": "AUDIT", "label": "Auditoría"},
    )
    assert create_response.status_code == 201
    work_order_type_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/work-order-types/{work_order_type_id}",
        headers=auth_headers(token_a),
        json={"label": "Auditoría técnica"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["label"] == "Auditoría técnica"
    assert update_response.json()["code"] == "AUDIT"


def test_duplicate_code_within_same_tenant_is_rejected(client, db_session):
    _, _, token_a, _ = _setup_two_tenants(client, db_session)

    response = client.post(
        "/api/v1/priorities",
        headers=auth_headers(token_a),
        json={"code": "LOW", "label": "Baja duplicada"},
    )

    assert response.status_code == 409


def test_same_code_is_allowed_across_different_tenants(client, db_session):
    _, _, token_a, token_b = _setup_two_tenants(client, db_session)

    response_a = client.post(
        "/api/v1/asset-types",
        headers=auth_headers(token_a),
        json={"code": "CHILLER", "label": "Chiller"},
    )
    response_b = client.post(
        "/api/v1/asset-types",
        headers=auth_headers(token_b),
        json={"code": "CHILLER", "label": "Enfriadora"},
    )

    assert response_a.status_code == 201
    assert response_b.status_code == 201


def test_work_order_status_code_is_not_editable_only_label_and_active(client, db_session):
    _, _, token_a, _ = _setup_two_tenants(client, db_session)

    statuses = client.get("/api/v1/work-order-statuses", headers=auth_headers(token_a)).json()
    pending = next(s for s in statuses if s["code"] == "PENDING")

    response = client.patch(
        f"/api/v1/work-order-statuses/{pending['id']}",
        headers=auth_headers(token_a),
        json={"label": "En cola", "active": False},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "PENDING"
    assert body["label"] == "En cola"
    assert body["active"] is False


def test_work_order_statuses_endpoint_has_no_create_route(client, db_session):
    """No debe existir forma de crear estados nuevos: el código es
    semántica interna fija (PRD §29, modelo-datos.md §4.11)."""
    _, _, token_a, _ = _setup_two_tenants(client, db_session)

    response = client.post(
        "/api/v1/work-order-statuses",
        headers=auth_headers(token_a),
        json={"code": "CUSTOM", "label": "Personalizado"},
    )

    assert response.status_code in (404, 405)


# ---------------------------------------------------------------------------
# Permisos por rol
# ---------------------------------------------------------------------------


def test_technician_can_read_but_not_manage_catalogs(client, db_session):
    _, _, token_a, _ = _setup_two_tenants(client, db_session)
    token_tech = _create_technician(client, token_a)

    read_response = client.get("/api/v1/priorities", headers=auth_headers(token_tech))
    assert read_response.status_code == 200

    write_response = client.post(
        "/api/v1/priorities",
        headers=auth_headers(token_tech),
        json={"code": "CRITICAL", "label": "Crítica"},
    )
    assert write_response.status_code == 403


def test_office_can_read_but_not_manage_catalogs(client, db_session):
    _, _, token_a, _ = _setup_two_tenants(client, db_session)

    client.post(
        "/api/v1/users",
        headers=auth_headers(token_a),
        json={
            "email": "oficina@stc.com.ar",
            "full_name": "Ana Gomez",
            "password": "Oficina123!",
            "role_code": "TENANT_OFFICE",
        },
    )
    token_office = login(client, "oficina@stc.com.ar", "Oficina123!")

    read_response = client.get("/api/v1/asset-types", headers=auth_headers(token_office))
    assert read_response.status_code == 200

    write_response = client.post(
        "/api/v1/asset-types",
        headers=auth_headers(token_office),
        json={"code": "SPLIT", "label": "Split"},
    )
    assert write_response.status_code == 403


def test_catalog_endpoints_require_authentication(client):
    assert client.get("/api/v1/priorities").status_code == 401
    assert client.get("/api/v1/asset-types").status_code == 401
    assert client.get("/api/v1/work-order-types").status_code == 401
    assert client.get("/api/v1/work-order-statuses").status_code == 401
