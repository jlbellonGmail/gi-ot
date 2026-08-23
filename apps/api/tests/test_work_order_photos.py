"""Pruebas de fotografías de OT (ROADMAP.md §06 — Mobile / PWA).

Cubre subida/listado/borrado, rechazo sobre OT terminal y aislamiento
multitenant del binario y del registro.
"""

import io
import shutil
import tempfile

import pytest

from tests.helpers import auth_headers, create_platform_owner, create_tenant_via_api, login
from tests.test_work_orders import _full_wo_setup

_JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"0" * 100  # cabecera JPEG mínima, contenido irrelevante


@pytest.fixture(autouse=True)
def _uploads_in_tmp(monkeypatch):
    """Redirige el storage de fotos a un directorio temporal para no
    escribir en `data/uploads` real durante los tests."""
    upload_dir = tempfile.mkdtemp(prefix="gi-ot-test-uploads-")

    class _FakeSettings:
        uploads_dir = upload_dir

    monkeypatch.setattr("app.services.work_order.get_settings", lambda: _FakeSettings())
    yield
    shutil.rmtree(upload_dir, ignore_errors=True)


def _setup_tenant_with_wo(client, db_session, admin_email="admin@stc.com.ar"):
    create_platform_owner(db_session)
    owner_token = login(client, "owner@gi-ot.com", "Owner123!")
    create_tenant_via_api(client, owner_token, "Servicio Tecnico Cordoba", admin_email, "AdminA123!")
    token = login(client, admin_email, "AdminA123!")
    payload = _full_wo_setup(client, token)
    wo = client.post("/api/v1/work-orders", headers=auth_headers(token), json=payload).json()
    return token, wo["id"]


def _upload(client, token, wo_id, filename="foto.jpg", content_type="image/jpeg", data=_JPEG_BYTES, caption=None):
    files = {"file": (filename, io.BytesIO(data), content_type)}
    form = {"caption": caption} if caption is not None else {}
    return client.post(
        f"/api/v1/work-orders/{wo_id}/photos", headers=auth_headers(token), files=files, data=form
    )


def test_upload_list_and_delete_photo(client, db_session):
    token, wo_id = _setup_tenant_with_wo(client, db_session)

    resp = _upload(client, token, wo_id, caption="Antes de la reparación")
    assert resp.status_code == 201, resp.text
    photo = resp.json()
    assert photo["work_order_id"] == wo_id
    assert photo["caption"] == "Antes de la reparación"

    listed = client.get(f"/api/v1/work-orders/{wo_id}/photos", headers=auth_headers(token)).json()
    assert len(listed) == 1
    assert listed[0]["id"] == photo["id"]

    file_resp = client.get(
        f"/api/v1/work-orders/{wo_id}/photos/{photo['id']}/file", headers=auth_headers(token)
    )
    assert file_resp.status_code == 200
    assert file_resp.content == _JPEG_BYTES

    del_resp = client.delete(
        f"/api/v1/work-orders/{wo_id}/photos/{photo['id']}", headers=auth_headers(token)
    )
    assert del_resp.status_code == 204

    listed_after = client.get(f"/api/v1/work-orders/{wo_id}/photos", headers=auth_headers(token)).json()
    assert listed_after == []


def test_reject_non_image_content_type(client, db_session):
    token, wo_id = _setup_tenant_with_wo(client, db_session)
    resp = _upload(client, token, wo_id, filename="doc.pdf", content_type="application/pdf", data=b"%PDF-1.4")
    assert resp.status_code == 400


def test_cannot_upload_or_delete_photo_on_terminal_wo(client, db_session):
    token, wo_id = _setup_tenant_with_wo(client, db_session)
    client.post(f"/api/v1/work-orders/{wo_id}/start", headers=auth_headers(token))
    client.post(
        f"/api/v1/work-orders/{wo_id}/finish",
        headers=auth_headers(token),
        json={"status_code": "UNRESOLVED"},
    )

    resp = _upload(client, token, wo_id)
    assert resp.status_code == 409


def test_photo_isolation_between_tenants(client, db_session):
    token_a, wo_id = _setup_tenant_with_wo(client, db_session, admin_email="admin@stc.com.ar")
    owner_token = login(client, "owner@gi-ot.com", "Owner123!")
    create_tenant_via_api(client, owner_token, "Ascensores del Litoral", "admin@adl.com.ar", "AdminB123!")
    token_b = login(client, "admin@adl.com.ar", "AdminB123!")

    photo = _upload(client, token_a, wo_id).json()

    assert client.get(f"/api/v1/work-orders/{wo_id}/photos", headers=auth_headers(token_b)).status_code == 404
    assert (
        client.get(
            f"/api/v1/work-orders/{wo_id}/photos/{photo['id']}/file", headers=auth_headers(token_b)
        ).status_code
        == 404
    )
    assert (
        client.delete(
            f"/api/v1/work-orders/{wo_id}/photos/{photo['id']}", headers=auth_headers(token_b)
        ).status_code
        == 404
    )
