import re
from datetime import date

PAYLOAD = {
    "company": "Acme Corp",
    "role": "Software Engineer",
    "status": "applied",
    "date_applied": str(date.today()),
}


def _extract_id(html: str) -> str:
    match = re.search(r'id="app-row-(\d+)"', html)
    assert match, "Could not find app-row ID in response HTML"
    return match.group(1)


def test_list_empty(client_a):
    r = client_a.get("/")
    assert r.status_code == 200


def test_create_returns_row(client_a):
    r = client_a.post("/applications", data=PAYLOAD)
    assert r.status_code == 200
    assert "Acme Corp" in r.text


def test_created_app_appears_in_list(client_a):
    client_a.post("/applications", data=PAYLOAD)
    r = client_a.get("/")
    assert "Acme Corp" in r.text


def test_edit_application(client_a):
    r = client_a.post("/applications", data=PAYLOAD)
    app_id = _extract_id(r.text)

    updated = {**PAYLOAD, "company": "Updated Corp", "role": "Senior Engineer"}
    r = client_a.put(f"/applications/{app_id}", data=updated)
    assert r.status_code == 200
    assert "Updated Corp" in r.text


def test_delete_application(client_a):
    r = client_a.post("/applications", data=PAYLOAD)
    app_id = _extract_id(r.text)

    r = client_a.delete(f"/applications/{app_id}")
    assert r.status_code == 200
    assert r.text.strip() == ""


def test_user_isolation_list(client_a, client_b):
    client_a.post("/applications", data=PAYLOAD)

    r_a = client_a.get("/")
    assert "Acme Corp" in r_a.text

    r_b = client_b.get("/")
    assert "Acme Corp" not in r_b.text


def test_user_isolation_row(client_a, client_b):
    r = client_a.post("/applications", data=PAYLOAD)
    app_id = _extract_id(r.text)

    r = client_b.get(f"/applications/{app_id}/edit")
    assert r.status_code == 404
