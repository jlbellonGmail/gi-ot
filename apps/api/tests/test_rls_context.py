import uuid

from app.db.rls import (
    set_authenticated_context,
    set_login_context,
    set_user_identity_context,
)


def test_rls_context_is_stored_without_postgresql_sql(db_session):
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    set_login_context(db_session, "User@Example.com")
    set_user_identity_context(db_session, user_id)
    set_authenticated_context(
        db_session,
        tenant_id=tenant_id,
        is_platform_admin=False,
    )

    assert db_session.info["rls_login_email"] == "user@example.com"
    assert db_session.info["rls_user_id"] == user_id
    assert db_session.info["rls_tenant_id"] == tenant_id
    assert db_session.info["rls_platform_admin"] is False
