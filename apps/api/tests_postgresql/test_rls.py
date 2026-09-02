import os
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

import pytest
from app.core.security import hash_password
from app.db.rls import set_authenticated_context, set_platform_context
from app.main import app
from app.models.asset_type import AssetType
from app.models.location import Asset, Location
from app.models.person import Customer, Person, PersonIdentification, Technician
from app.models.priority import Priority
from app.models.role import TENANT_ADMIN, Role
from app.models.sync_operation import SyncOperation
from app.models.tenant import Tenant, TenantConfig
from app.models.user import User
from app.models.work_order import (
    HistoryEventType,
    WorkOrder,
    WorkOrderHistory,
    WorkOrderPhoto,
)
from app.models.work_order_receipt import WorkOrderReceipt
from app.models.work_order_status import WorkOrderStatus
from app.models.work_order_type import WorkOrderType
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("POSTGRES_RLS_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="POSTGRES_RLS_DATABASE_URL es requerido para tests RLS reales",
)

engine = create_engine(DATABASE_URL or "sqlite:///:memory:")
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)

TENANT_TABLES = (
    "tenant_configs",
    "people",
    "person_identifications",
    "customers",
    "technicians",
    "locations",
    "assets",
    "asset_types",
    "priorities",
    "work_order_statuses",
    "work_order_types",
    "work_orders",
    "work_order_history",
    "work_order_photos",
    "work_order_receipts",
    "sync_operations",
)


def _graph(
    session: Session, tenant: Tenant, role: Role, suffix: str
) -> dict[str, uuid.UUID]:
    admin = User(
        tenant_id=tenant.id,
        role_id=role.id,
        email=f"admin-{suffix}@example.com",
        password_hash=hash_password("RlsPass123!"),
        full_name=f"Admin {suffix}",
    )
    config = TenantConfig(
        tenant_id=tenant.id, commercial_display_name=f"Tenant {suffix}"
    )
    customer_person = Person(tenant_id=tenant.id, display_name=f"Customer {suffix}")
    technician_person = Person(tenant_id=tenant.id, display_name=f"Technician {suffix}")
    session.add_all([admin, config, customer_person, technician_person])
    session.flush()

    identification = PersonIdentification(
        tenant_id=tenant.id,
        person_id=customer_person.id,
        country_code="AR",
        identification_type="DNI",
        identification_value=f"ID-{suffix}",
        is_primary=True,
    )
    customer = Customer(tenant_id=tenant.id, person_id=customer_person.id)
    technician = Technician(tenant_id=tenant.id, person_id=technician_person.id)
    asset_type = AssetType(tenant_id=tenant.id, code="EQUIPMENT", label="Equipo")
    priority = Priority(
        tenant_id=tenant.id, code="NORMAL", label="Normal", sort_order=1
    )
    status = WorkOrderStatus(
        tenant_id=tenant.id,
        code="PENDING",
        label="Pendiente",
        sort_order=1,
    )
    work_type = WorkOrderType(tenant_id=tenant.id, code="REPAIR", label="Reparación")
    session.add_all(
        [identification, customer, technician, asset_type, priority, status, work_type]
    )
    session.flush()

    location = Location(
        tenant_id=tenant.id,
        customer_id=customer_person.id,
        name=f"Location {suffix}",
    )
    session.add(location)
    session.flush()
    asset = Asset(
        tenant_id=tenant.id,
        location_id=location.id,
        asset_type_id=asset_type.id,
        name=f"Asset {suffix}",
        qr_code=f"QR-SHARED-{suffix}",
    )
    session.add(asset)
    session.flush()

    work_order = WorkOrder(
        tenant_id=tenant.id,
        number=1,
        customer_id=customer_person.id,
        location_id=location.id,
        asset_id=asset.id,
        technician_id=technician_person.id,
        work_order_type_id=work_type.id,
        priority_id=priority.id,
        status_id=status.id,
        requested_description=f"Repair {suffix}",
        created_by=admin.id,
    )
    session.add(work_order)
    session.flush()
    session.add_all(
        [
            WorkOrderHistory(
                tenant_id=tenant.id,
                work_order_id=work_order.id,
                event_type=HistoryEventType.CREATED,
                performed_by=admin.id,
            ),
            WorkOrderPhoto(
                tenant_id=tenant.id,
                work_order_id=work_order.id,
                storage_key=f"{tenant.id}/work-orders/{work_order.id}/photos/test.jpg",
                uploaded_by=admin.id,
            ),
            WorkOrderReceipt(
                tenant_id=tenant.id,
                work_order_id=work_order.id,
                content_html="<p>receipt</p>",
                generated_by=admin.id,
            ),
            SyncOperation(
                tenant_id=tenant.id,
                operation_type="update_wo",
                entity_id=work_order.id,
                payload="{}",
            ),
        ]
    )
    session.flush()
    return {
        "tenant": tenant.id,
        "admin": admin.id,
        "person": customer_person.id,
        "location": location.id,
        "asset_type": asset_type.id,
    }


@pytest.fixture(scope="module")
def graphs() -> dict[str, dict[str, uuid.UUID]]:
    with TestingSession() as session:
        set_platform_context(session)
        role = session.scalar(select(Role).where(Role.code == TENANT_ADMIN))
        assert role is not None
        tenant_a = Tenant(name="RLS Tenant A")
        tenant_b = Tenant(name="RLS Tenant B")
        session.add_all([tenant_a, tenant_b])
        session.flush()
        result = {
            "a": _graph(session, tenant_a, role, "a"),
            "b": _graph(session, tenant_b, role, "b"),
        }
        session.commit()
        return result


@contextmanager
def _tenant_session(tenant_id: uuid.UUID) -> Iterator[Session]:
    with TestingSession() as session:
        set_authenticated_context(
            session,
            tenant_id=tenant_id,
            is_platform_admin=False,
        )
        yield session


def test_rls_catalog_and_connection_role_are_effective(graphs):
    with TestingSession() as session:
        role_state = session.execute(
            text(
                "SELECT rolsuper, rolbypassrls FROM pg_roles "
                "WHERE rolname = current_user"
            )
        ).one()
        assert role_state == (False, False)

        rows = session.execute(
            text(
                "SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity "
                "FROM pg_class c WHERE c.relname = ANY(:tables)"
            ),
            {"tables": [*TENANT_TABLES, "tenants", "users"]},
        ).all()
        assert len(rows) == len(TENANT_TABLES) + 2
        assert all(enabled and forced for _name, enabled, forced in rows)

        policy_tables = set(
            session.execute(
                text(
                    "SELECT DISTINCT tablename FROM pg_policies WHERE schemaname='public'"
                )
            ).scalars()
        )
        assert {*TENANT_TABLES, "tenants", "users"} <= policy_tables


def test_direct_select_without_orm_filter_is_tenant_isolated(graphs):
    for current, hidden in (("a", "b"), ("b", "a")):
        with _tenant_session(graphs[current]["tenant"]) as session:
            visible_people = set(
                session.execute(text("SELECT tenant_id FROM people")).scalars()
            )
            assert visible_people == {graphs[current]["tenant"]}
            assert graphs[hidden]["tenant"] not in visible_people

            for table in TENANT_TABLES:
                visible_tenants = set(
                    session.execute(text(f'SELECT tenant_id FROM "{table}"')).scalars()
                )
                assert visible_tenants <= {graphs[current]["tenant"]}


def test_direct_cross_tenant_insert_update_and_delete_are_blocked(graphs):
    with _tenant_session(graphs["a"]["tenant"]) as session:
        with pytest.raises(DBAPIError):
            session.execute(
                text(
                    "INSERT INTO people "
                    "(id, tenant_id, person_type, display_name, status, created_at, updated_at) "
                    "VALUES (:id, :tenant, 'INDIVIDUAL', 'Fraud', 'ACTIVE', :now, :now)"
                ),
                {
                    "id": uuid.uuid4(),
                    "tenant": graphs["b"]["tenant"],
                    "now": datetime.now(timezone.utc),
                },
            )
        session.rollback()

        updated = session.execute(
            text("UPDATE people SET display_name='Compromised' WHERE id=:id"),
            {"id": graphs["b"]["person"]},
        )
        assert updated.rowcount == 0
        session.commit()

        deleted = session.execute(
            text("DELETE FROM people WHERE id=:id"),
            {"id": graphs["b"]["person"]},
        )
        assert deleted.rowcount == 0


def test_composite_fk_blocks_cross_tenant_reference(graphs):
    with (
        _tenant_session(graphs["a"]["tenant"]) as session,
        pytest.raises(IntegrityError),
    ):
        session.execute(
            text(
                "INSERT INTO assets "
                "(id, tenant_id, location_id, asset_type_id, name, status, created_at, updated_at) "
                "VALUES (:id, :tenant, :location, :asset_type, 'Fraud', 'ACTIVE', :now, :now)"
            ),
            {
                "id": uuid.uuid4(),
                "tenant": graphs["a"]["tenant"],
                "location": graphs["b"]["location"],
                "asset_type": graphs["a"]["asset_type"],
                "now": datetime.now(timezone.utc),
            },
        )


def test_fastapi_login_and_post_commit_context_survive_rls(graphs):
    client = TestClient(app)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin-a@example.com", "password": "RlsPass123!"},
    )
    assert login.status_code == 200, login.text
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    assert me.json()["tenant_id"] == str(graphs["a"]["tenant"])

    created = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "email": "second-a@example.com",
            "full_name": "Second A",
            "password": "SecondPass123!",
            "role_code": "TENANT_OFFICE",
        },
    )
    assert created.status_code == 201, created.text

    users = client.get("/api/v1/users", headers=headers)
    assert users.status_code == 200, users.text
    assert {item["email"] for item in users.json()} == {
        "admin-a@example.com",
        "second-a@example.com",
    }
