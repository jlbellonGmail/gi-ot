"""Pruebas del modelo de plantillas de configuración inicial por tenant
(ROADMAP.md §02 — "Seed inicial por tenant").

La plantilla `ConfigTemplate` (código `DEFAULT`) contiene los valores
estándar de estados de OT, prioridades, tipos de trabajo y tipos de
activo. Al crear un tenant, `app.core.provisioning.provision_tenant_from_template`
copia esos valores a la configuración propia del tenant. Estas pruebas
verifican que la plantilla nunca se modifica ni se comparte entre tenants,
y que el provisionamiento es idempotente.
"""

import uuid

from sqlalchemy import select

from app.core.provisioning import provision_tenant_from_template
from app.models.asset_type import AssetType
from app.models.config_template import DEFAULT_TEMPLATE_CODE, ConfigTemplate
from app.models.priority import Priority
from app.models.template_asset_type import TemplateAssetType
from app.models.template_priority import TemplatePriority
from app.models.template_work_order_status import TemplateWorkOrderStatus
from app.models.template_work_order_type import TemplateWorkOrderType
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


def _template_counts(db_session, template_id):
    return {
        "priorities": len(
            db_session.scalars(select(TemplatePriority).where(TemplatePriority.template_id == template_id)).all()
        ),
        "work_order_types": len(
            db_session.scalars(
                select(TemplateWorkOrderType).where(TemplateWorkOrderType.template_id == template_id)
            ).all()
        ),
        "work_order_statuses": len(
            db_session.scalars(
                select(TemplateWorkOrderStatus).where(TemplateWorkOrderStatus.template_id == template_id)
            ).all()
        ),
        "asset_types": len(
            db_session.scalars(select(TemplateAssetType).where(TemplateAssetType.template_id == template_id)).all()
        ),
    }


def _tenant_counts(db_session, tenant_id):
    return {
        "priorities": len(db_session.scalars(select(Priority).where(Priority.tenant_id == tenant_id)).all()),
        "work_order_types": len(
            db_session.scalars(select(WorkOrderType).where(WorkOrderType.tenant_id == tenant_id)).all()
        ),
        "work_order_statuses": len(
            db_session.scalars(select(WorkOrderStatus).where(WorkOrderStatus.tenant_id == tenant_id)).all()
        ),
        "asset_types": len(db_session.scalars(select(AssetType).where(AssetType.tenant_id == tenant_id)).all()),
    }


# ---------------------------------------------------------------------------
# 1. Un tenant nuevo recibe los valores DEFAULT
# ---------------------------------------------------------------------------


def test_new_tenant_receives_default_template_values(client, db_session):
    template = db_session.scalar(select(ConfigTemplate).where(ConfigTemplate.code == DEFAULT_TEMPLATE_CODE))
    assert template is not None

    tenant_a, _, token_a, _ = _setup_two_tenants(client, db_session)

    priorities = client.get("/api/v1/priorities", headers=auth_headers(token_a)).json()
    work_order_types = client.get("/api/v1/work-order-types", headers=auth_headers(token_a)).json()
    statuses = client.get("/api/v1/work-order-statuses", headers=auth_headers(token_a)).json()
    asset_types = client.get("/api/v1/asset-types", headers=auth_headers(token_a)).json()

    template_priority_codes = {
        p.code for p in db_session.scalars(select(TemplatePriority).where(TemplatePriority.template_id == template.id))
    }
    template_work_order_type_codes = {
        t.code
        for t in db_session.scalars(
            select(TemplateWorkOrderType).where(TemplateWorkOrderType.template_id == template.id)
        )
    }
    template_status_codes = {
        s.code
        for s in db_session.scalars(
            select(TemplateWorkOrderStatus).where(TemplateWorkOrderStatus.template_id == template.id)
        )
    }
    template_asset_type_codes = {
        a.code
        for a in db_session.scalars(select(TemplateAssetType).where(TemplateAssetType.template_id == template.id))
    }

    assert {p["code"] for p in priorities} == template_priority_codes
    assert {t["code"] for t in work_order_types} == template_work_order_type_codes
    assert {s["code"] for s in statuses} == template_status_codes
    assert {a["code"] for a in asset_types} == template_asset_type_codes
    assert all(p["tenant_id"] == tenant_a["id"] for p in priorities)


# ---------------------------------------------------------------------------
# 2. Dos tenants reciben copias independientes
# ---------------------------------------------------------------------------


def test_two_tenants_receive_independent_copies_of_the_template(client, db_session):
    tenant_a, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    priorities_a = client.get("/api/v1/priorities", headers=auth_headers(token_a)).json()
    priorities_b = client.get("/api/v1/priorities", headers=auth_headers(token_b)).json()

    ids_a = {p["id"] for p in priorities_a}
    ids_b = {p["id"] for p in priorities_b}

    # Mismos códigos (misma plantilla de origen), pero filas físicamente
    # distintas: cada tenant es dueño de su propia copia.
    assert {p["code"] for p in priorities_a} == {p["code"] for p in priorities_b}
    assert ids_a.isdisjoint(ids_b)
    assert all(p["tenant_id"] == tenant_a["id"] for p in priorities_a)
    assert all(p["tenant_id"] == tenant_b["id"] for p in priorities_b)


# ---------------------------------------------------------------------------
# 3. Modificar Tenant A no modifica Tenant B ni la plantilla
# ---------------------------------------------------------------------------


def test_modifying_tenant_a_does_not_affect_tenant_b_or_the_template(client, db_session):
    template = db_session.scalar(select(ConfigTemplate).where(ConfigTemplate.code == DEFAULT_TEMPLATE_CODE))
    template_pending_before = db_session.scalar(
        select(TemplateWorkOrderStatus).where(
            TemplateWorkOrderStatus.template_id == template.id, TemplateWorkOrderStatus.code == "PENDING"
        )
    )
    original_template_label = template_pending_before.label

    _, tenant_b, token_a, token_b = _setup_two_tenants(client, db_session)

    statuses_a = client.get("/api/v1/work-order-statuses", headers=auth_headers(token_a)).json()
    pending_a = next(s for s in statuses_a if s["code"] == "PENDING")

    client.patch(
        f"/api/v1/work-order-statuses/{pending_a['id']}",
        headers=auth_headers(token_a),
        json={"label": "Modificado por A"},
    )

    # Tenant B no ve el cambio.
    statuses_b = client.get("/api/v1/work-order-statuses", headers=auth_headers(token_b)).json()
    pending_b = next(s for s in statuses_b if s["code"] == "PENDING")
    assert pending_b["label"] == "Pendiente"
    assert pending_b["tenant_id"] == tenant_b["id"]

    # La plantilla tampoco cambió.
    db_session.expire_all()
    template_pending_after = db_session.scalar(
        select(TemplateWorkOrderStatus).where(
            TemplateWorkOrderStatus.template_id == template.id, TemplateWorkOrderStatus.code == "PENDING"
        )
    )
    assert template_pending_after.label == original_template_label


# ---------------------------------------------------------------------------
# 4. Volver a ejecutar la inicialización no duplica datos
# ---------------------------------------------------------------------------


def test_running_provisioning_again_does_not_duplicate_data(client, db_session):
    tenant_a, _, _, _ = _setup_two_tenants(client, db_session)
    tenant_id = uuid.UUID(tenant_a["id"])

    template = db_session.scalar(select(ConfigTemplate).where(ConfigTemplate.code == DEFAULT_TEMPLATE_CODE))
    template_counts_before = _template_counts(db_session, template.id)
    tenant_counts_before = _tenant_counts(db_session, tenant_id)

    provision_tenant_from_template(db_session, tenant_id)
    provision_tenant_from_template(db_session, tenant_id)
    provision_tenant_from_template(db_session, tenant_id)
    db_session.commit()

    # El tenant no acumula filas duplicadas...
    assert _tenant_counts(db_session, tenant_id) == tenant_counts_before
    # ...y la plantilla, que nunca se escribe durante el provisionamiento,
    # tampoco cambia.
    assert _template_counts(db_session, template.id) == template_counts_before


def test_provisioning_a_second_tenant_does_not_alter_the_template(client, db_session):
    """La plantilla es de solo lectura desde el punto de vista del
    provisionamiento: crear más tenants nunca le agrega ni le quita filas."""
    template = db_session.scalar(select(ConfigTemplate).where(ConfigTemplate.code == DEFAULT_TEMPLATE_CODE))
    template_counts_before = _template_counts(db_session, template.id)

    _setup_two_tenants(client, db_session)

    assert _template_counts(db_session, template.id) == template_counts_before
