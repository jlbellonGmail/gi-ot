from tests.helpers import auth_headers, create_platform_owner, login


def test_login_success(client, db_session):
    create_platform_owner(db_session, "owner@gi-ot.com", "Owner123!")

    response = client.post(
        "/api/v1/auth/login", json={"email": "owner@gi-ot.com", "password": "Owner123!"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_is_rejected(client, db_session):
    create_platform_owner(db_session, "owner@gi-ot.com", "Owner123!")

    response = client.post(
        "/api/v1/auth/login", json={"email": "owner@gi-ot.com", "password": "wrong"}
    )

    assert response.status_code == 401


def test_login_unknown_user_is_rejected(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": "nadie@gi-ot.com", "password": "x"}
    )

    assert response.status_code == 401


def test_me_requires_valid_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    response = client.get("/api/v1/auth/me", headers=auth_headers("token-invalido"))
    assert response.status_code == 401


def test_me_returns_current_user(client, db_session):
    create_platform_owner(db_session, "owner@gi-ot.com", "Owner123!")
    token = login(client, "owner@gi-ot.com", "Owner123!")

    response = client.get("/api/v1/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "owner@gi-ot.com"
    assert body["role_code"] == "PLATFORM_OWNER"
    assert body["tenant_id"] is None
