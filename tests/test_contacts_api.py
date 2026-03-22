from fastapi.testclient import TestClient

from signaldesk.security import decode_access_token


def _register_token(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    return r.json()["access_token"]


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_contacts_crud_for_authenticated_user(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "owner@example.com", "secret123")
    uid = int(decode_access_token(token)["sub"])
    h = _bearer(token)

    listed = auth_client.get("/contacts", headers=h)
    assert listed.status_code == 200
    assert listed.json() == []

    assert auth_client.post("/contacts", json={"name": "nope"}).status_code == 401

    created = auth_client.post("/contacts", headers=h, json={"name": "Acme"})
    assert created.status_code == 201
    row = created.json()
    cid = row["id"]
    assert row["name"] == "Acme"
    assert row["owner_id"] == uid

    listed2 = auth_client.get("/contacts", headers=h)
    assert listed2.status_code == 200
    assert len(listed2.json()) == 1

    one = auth_client.get(f"/contacts/{cid}", headers=h)
    assert one.status_code == 200
    assert one.json()["name"] == "Acme"

    patched = auth_client.patch(f"/contacts/{cid}", headers=h, json={"name": "Acme II"})
    assert patched.status_code == 200
    assert patched.json()["name"] == "Acme II"

    deleted = auth_client.delete(f"/contacts/{cid}", headers=h)
    assert deleted.status_code == 204

    missing = auth_client.get(f"/contacts/{cid}", headers=h)
    assert missing.status_code == 404


def test_contacts_list_requires_auth(auth_client: TestClient) -> None:
    assert auth_client.get("/contacts").status_code == 401


def test_contact_other_user_returns_404(auth_client: TestClient) -> None:
    ta = _register_token(auth_client, "alice@example.com", "a")
    tb = _register_token(auth_client, "bob@example.com", "b")
    c = auth_client.post(
        "/contacts",
        headers=_bearer(ta),
        json={"name": "Alice only"},
    )
    assert c.status_code == 201
    cid = c.json()["id"]

    r = auth_client.get(f"/contacts/{cid}", headers=_bearer(tb))
    assert r.status_code == 404

    r2 = auth_client.patch(
        f"/contacts/{cid}",
        headers=_bearer(tb),
        json={"name": "hijack"},
    )
    assert r2.status_code == 404

    r3 = auth_client.delete(f"/contacts/{cid}", headers=_bearer(tb))
    assert r3.status_code == 404

    still = auth_client.get(f"/contacts/{cid}", headers=_bearer(ta))
    assert still.status_code == 200
