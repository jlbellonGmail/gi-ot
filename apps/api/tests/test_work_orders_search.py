"""Pruebas del listado operativo de OT (búsqueda + filtros + orden,
ROADMAP.md §07, UI-UX-STANDARDS.md §10) — GET /work-orders con
`q`, `priority_id`, `location_id`, `asset_id`, `date_from`/`date_to` y `sort`.
"""

from tests.helpers import auth_headers
from tests.test_work_orders import _full_wo_setup, _setup_two_tenants


def _priority_id_by_code(client, token, code):
    resp = client.get("/api/v1/priorities", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    for p in resp.json():
        if p["code"] == code:
            return p["id"]
    raise AssertionError(f"No se encontró prioridad {code}")


def test_search_by_customer_name(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    payload1 = _full_wo_setup(client, token_a, "Rodriguez")
    payload2 = _full_wo_setup(client, token_a, "Gomez")
    client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload1)
    client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload2)

    resp = client.get("/api/v1/work-orders?q=Rodriguez", headers=auth_headers(token_a))
    assert resp.status_code == 200, resp.text
    results = resp.json()
    assert len(results) == 1
    assert results[0]["customer_id"] == payload1["customer_id"]


def test_search_by_wo_number(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    payload = _full_wo_setup(client, token_a)
    wo = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload).json()

    resp = client.get(f"/api/v1/work-orders?q={wo['number']}", headers=auth_headers(token_a))
    assert resp.status_code == 200, resp.text
    assert any(w["id"] == wo["id"] for w in resp.json())


def test_filter_by_priority_and_location(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    payload1 = _full_wo_setup(client, token_a, "1")
    payload2 = _full_wo_setup(client, token_a, "2")
    payload1["priority_id"] = _priority_id_by_code(client, token_a, "URGENT")
    payload2["priority_id"] = _priority_id_by_code(client, token_a, "LOW")

    wo1 = client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload1).json()
    client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload2)

    resp = client.get(
        f"/api/v1/work-orders?priority_id={payload1['priority_id']}", headers=auth_headers(token_a)
    )
    assert resp.status_code == 200, resp.text
    results = resp.json()
    assert len(results) == 1
    assert results[0]["id"] == wo1["id"]

    resp2 = client.get(
        f"/api/v1/work-orders?location_id={payload2['location_id']}", headers=auth_headers(token_a)
    )
    assert resp2.status_code == 200, resp2.text
    assert len(resp2.json()) == 1
    assert resp2.json()[0]["location_id"] == payload2["location_id"]


def test_sort_by_priority(client, db_session):
    _, _, _, token_a, _ = _setup_two_tenants(client, db_session)
    payload_low = _full_wo_setup(client, token_a, "1")
    payload_urgent = _full_wo_setup(client, token_a, "2")
    payload_low["priority_id"] = _priority_id_by_code(client, token_a, "LOW")
    payload_urgent["priority_id"] = _priority_id_by_code(client, token_a, "URGENT")

    client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload_low)
    client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload_urgent)

    resp = client.get("/api/v1/work-orders?sort=priority", headers=auth_headers(token_a))
    assert resp.status_code == 200, resp.text
    results = resp.json()
    assert results[0]["priority_code"] == "URGENT"


def test_search_and_filters_isolated_between_tenants(client, db_session):
    _, _, _, token_a, token_b = _setup_two_tenants(client, db_session)
    payload_a = _full_wo_setup(client, token_a, "Compartido")
    payload_b = _full_wo_setup(client, token_b, "Compartido")
    client.post("/api/v1/work-orders", headers=auth_headers(token_a), json=payload_a)
    client.post("/api/v1/work-orders", headers=auth_headers(token_b), json=payload_b)

    resp = client.get("/api/v1/work-orders?q=Compartido", headers=auth_headers(token_a))
    assert resp.status_code == 200, resp.text
    results = resp.json()
    assert len(results) == 1
    assert results[0]["customer_id"] == payload_a["customer_id"]
