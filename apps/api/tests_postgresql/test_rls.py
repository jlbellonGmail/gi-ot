"""Pruebas directas de RLS sobre una base PostgreSQL migrada."""

import os
import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

from app.db.rls import (
    set_authenticated_context,
    set_login_context,
    set_platform_context,
)
from app.models.person import Person, PersonType
from app.models.role import PLATFORM_OWNER, TENANT_ADMIN, Role
from app.models.tenant import Tenant
from app.models.user import User

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL", "").startswith("postgresql"),
    reason="requiere PostgreSQL migrado",
)


@pytest.fixture(scope="module")
def rls_session():
    database_url = os.environ["DATABASE_URL"]
    engine = create_engine(database_url)
    session = Session(engine)
    platform_role = session.scalar(select(Role).where(Role.code == PLATFORM_OWNER))
    admin_role = session.scalar(select(Role).where(Role.code == TENANT_ADMIN))
    assert platform_role is not None
    assert admin_role is not None
    set_platform_context(session)
    tenant_a = Tenant(id=uuid.uuid4(), name="RLS A")
    tenant_b = Tenant(id=uuid.uuid4(), name="RLS B")
    session.add_all([tenant_a, tenant_b])
    session.flush()
    user_a = User(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        role_id=admin_role.id,
        email="rls-a@example.test",
        password_hash="hash",
        full_name="RLS A",
    )
    owner = User(
        id=uuid.uuid4(),
        tenant_id=None,
        role_id=platform_role.id,
        email="rls-owner@example.test",
        password_hash="hash",
        full_name="RLS Owner",
    )
    session.add_all([user_a, owner])
    session.commit()
    try:
        yield session, tenant_a.id, tenant_b.id, owner.email
    finally:
        session.rollback()
        set_platform_context(session)
        session.query(User).delete(synchronize_session=False)
        session.query(Tenant).delete(synchronize_session=False)
        session.commit()
        session.close()
        engine.dispose()


def test_tenant_context_allows_own_rows_and_hides_other_tenant(rls_session):
    session, tenant_a, tenant_b, _ = rls_session
    set_authenticated_context(session, tenant_id=tenant_a, is_platform_admin=False)
    own = session.scalar(select(Tenant).where(Tenant.id == tenant_a))
    other = session.scalar(select(Tenant).where(Tenant.id == tenant_b))
    assert own is not None
    assert other is None


def test_rls_rejects_cross_tenant_insert_and_allows_same_tenant_after_rollback(rls_session):
    session, tenant_a, tenant_b, _ = rls_session
    set_authenticated_context(session, tenant_id=tenant_a, is_platform_admin=False)
    session.add(
        Person(
            tenant_id=tenant_b,
            person_type=PersonType.INDIVIDUAL,
            display_name="Cross tenant",
        )
    )
    with pytest.raises(DBAPIError):
        session.flush()
    session.rollback()
    set_authenticated_context(session, tenant_id=tenant_a, is_platform_admin=False)
    session.add(
        Person(
            tenant_id=tenant_a,
            person_type=PersonType.INDIVIDUAL,
            display_name="Same tenant",
        )
    )
    session.commit()


def test_platform_owner_login_context_can_read_platform_user(rls_session):
    session, _, _, owner_email = rls_session
    set_login_context(session, owner_email)
    owner = session.scalar(select(User).where(User.email == owner_email))
    assert owner is not None
    assert owner.tenant_id is None
