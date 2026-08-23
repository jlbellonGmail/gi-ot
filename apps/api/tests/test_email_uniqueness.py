"""Unicidad de email: global para PLATFORM_OWNER, por tenant para el resto.

Cubre el riesgo detectado al cerrar Etapa 01: un UNIQUE compuesto
(tenant_id, email) no evita duplicados entre filas con tenant_id NULL,
porque SQL trata cada NULL como distinto en un índice único.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.models.role import PLATFORM_OWNER, Role
from app.models.user import User
from tests.helpers import auth_headers, create_platform_owner, create_tenant_via_api, login
from sqlalchemy import select


def test_cannot_create_two_platform_owners_with_same_email(db_session):
    create_platform_owner(db_session, "owner@gi-ot.com", "Owner123!")

    role = db_session.scalar(select(Role).where(Role.code == PLATFORM_OWNER))
    duplicate = User(
        tenant_id=None,
        role_id=role.id,
        email="owner@gi-ot.com",
        full_name="Otro Owner",
        password_hash=hash_password("Otro123!"),
    )
    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_two_tenants_can_reuse_same_admin_email_but_not_within_same_tenant(client, db_session):
    """El aislamiento por tenant no debe verse afectado por el fix: dos
    tenants distintos pueden tener un usuario con el mismo email, pero dos
    usuarios del mismo tenant no.
    """
    create_platform_owner(db_session, "owner@gi-ot.com", "Owner123!")
    owner_token = login(client, "owner@gi-ot.com", "Owner123!")

    tenant_a = create_tenant_via_api(
        client, owner_token, "Servicio Tecnico Cordoba", "compartido@ejemplo.com", "AdminA123!"
    )
    # Mismo email de admin en otro tenant: debe permitirse (no es global).
    tenant_b = create_tenant_via_api(
        client, owner_token, "Ascensores del Litoral", "compartido@ejemplo.com", "AdminB123!"
    )
    assert tenant_a["id"] != tenant_b["id"]

    token_a = login(client, "compartido@ejemplo.com", "AdminA123!")

    # Repetir el mismo email dentro del tenant A sí debe rechazarse.
    response = client.post(
        "/api/v1/users",
        headers=auth_headers(token_a),
        json={
            "email": "compartido@ejemplo.com",
            "full_name": "Duplicado",
            "password": "x1234567",
            "role_code": "TENANT_TECHNICIAN",
        },
    )
    assert response.status_code == 409


def test_platform_owner_email_cannot_collide_with_signup_creation_path(db_session):
    """Aunque no exista endpoint HTTP para crear PLATFORM_OWNER, la
    restricción vive en el modelo de datos: dos altas directas con el mismo
    email deben fallar sin importar el punto de entrada.
    """
    create_platform_owner(db_session, "unico@gi-ot.com", "Pass123!")

    role = db_session.scalar(select(Role).where(Role.code == PLATFORM_OWNER))
    db_session.add(
        User(
            tenant_id=None,
            role_id=role.id,
            email="unico@gi-ot.com",
            full_name="Segundo intento",
            password_hash=hash_password("Pass456!"),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
