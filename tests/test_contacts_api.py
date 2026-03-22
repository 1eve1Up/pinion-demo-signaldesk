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


def test_contact_create_with_email_phone_company(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "crm@example.com", "secret123")
    h = _bearer(token)
    r = auth_client.post(
        "/contacts",
        headers=h,
        json={
            "name": "Full Co",
            "email": "full@example.com",
            "phone": "+1 555 0100",
            "company": "Full Co LLC",
        },
    )
    assert r.status_code == 201
    row = r.json()
    assert row["name"] == "Full Co"
    assert row["email"] == "full@example.com"
    assert row["phone"] == "+1 555 0100"
    assert row["company"] == "Full Co LLC"


def test_contact_patch_clears_optional_fields_with_null(
    auth_client: TestClient,
) -> None:
    token = _register_token(auth_client, "patch@example.com", "secret123")
    h = _bearer(token)
    c = auth_client.post(
        "/contacts",
        headers=h,
        json={
            "name": "Tmp",
            "email": "tmp@example.com",
            "company": "Acme",
        },
    )
    assert c.status_code == 201
    cid = c.json()["id"]

    cleared = auth_client.patch(
        f"/contacts/{cid}",
        headers=h,
        json={"email": None, "company": None},
    )
    assert cleared.status_code == 200
    row = cleared.json()
    assert row["email"] is None
    assert row["company"] is None
    assert row["name"] == "Tmp"


def test_contact_invalid_email_returns_422(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "bad@example.com", "secret123")
    r = auth_client.post(
        "/contacts",
        headers=_bearer(token),
        json={"name": "X", "email": "not-an-email"},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"


def test_contact_phone_too_long_returns_422(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "long@example.com", "secret123")
    r = auth_client.post(
        "/contacts",
        headers=_bearer(token),
        json={"name": "X", "phone": "x" * 51},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"


def test_contact_patch_name_null_returns_422(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "nullname@example.com", "secret123")
    h = _bearer(token)
    c = auth_client.post("/contacts", headers=h, json={"name": "Keep"})
    cid = c.json()["id"]
    r = auth_client.patch(f"/contacts/{cid}", headers=h, json={"name": None})
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "validation_error"
    assert "null" in body["message"].lower()
