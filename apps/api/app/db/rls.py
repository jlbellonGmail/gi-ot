"""Contexto transaccional para Row-Level Security de PostgreSQL.

SQLite ignora este módulo. En PostgreSQL los valores se conservan en
``Session.info`` y se aplican al comenzar cada transacción para sobrevivir a
commits intermedios dentro de una misma request.
"""

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import event, func, select
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

_CONTEXT_SETTINGS: Mapping[str, str] = {
    "rls_user_id": "app.user_id",
    "rls_tenant_id": "app.tenant_id",
    "rls_login_email": "app.login_email",
    "rls_platform_admin": "app.platform_admin",
}


def _render(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _apply_to_connection(session: Session, connection: Connection) -> None:
    if connection.dialect.name != "postgresql":
        return
    for info_key, setting_name in _CONTEXT_SETTINGS.items():
        connection.execute(
            select(func.set_config(setting_name, _render(session.info.get(info_key)), True))
        )


@event.listens_for(Session, "after_begin")
def _set_rls_context_after_begin(
    session: Session, _transaction: object, connection: Connection
) -> None:
    _apply_to_connection(session, connection)


def _set_context_value(session: Session, info_key: str, value: Any) -> None:
    session.info[info_key] = value
    bind = session.get_bind()
    if bind.dialect.name != "postgresql" or not session.in_transaction():
        return
    session.execute(
        select(func.set_config(_CONTEXT_SETTINGS[info_key], _render(value), True))
    )


def set_login_context(session: Session, email: str) -> None:
    _set_context_value(session, "rls_login_email", email.strip().lower())


def set_user_identity_context(session: Session, user_id: UUID) -> None:
    _set_context_value(session, "rls_user_id", user_id)


def set_authenticated_context(
    session: Session, *, tenant_id: UUID | None, is_platform_admin: bool
) -> None:
    _set_context_value(session, "rls_tenant_id", tenant_id)
    _set_context_value(session, "rls_platform_admin", is_platform_admin)


def set_platform_context(session: Session) -> None:
    set_authenticated_context(session, tenant_id=None, is_platform_admin=True)
