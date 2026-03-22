from fastapi.testclient import TestClient


def _register_token(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    return r.json()["access_token"]


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_notes_crud_on_owned_contact(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "owner@example.com", "secret123")
    h = _bearer(token)
    c = auth_client.post("/contacts", headers=h, json={"name": "Acme"})
    assert c.status_code == 201
    cid = c.json()["id"]

    listed = auth_client.get(f"/contacts/{cid}/notes", headers=h)
    assert listed.status_code == 200
    assert listed.json() == []

    assert (
        auth_client.post(f"/contacts/{cid}/notes", json={"body": "x"}).status_code
        == 401
    )

    created = auth_client.post(
        f"/contacts/{cid}/notes", headers=h, json={"body": "First touch"}
    )
    assert created.status_code == 201
    row = created.json()
    nid = row["id"]
    assert row["contact_id"] == cid
    assert row["body"] == "First touch"

    listed2 = auth_client.get(f"/contacts/{cid}/notes", headers=h)
    assert listed2.status_code == 200
    assert len(listed2.json()) == 1

    one = auth_client.get(f"/contacts/{cid}/notes/{nid}", headers=h)
    assert one.status_code == 200
    assert one.json()["body"] == "First touch"

    patched = auth_client.patch(
        f"/contacts/{cid}/notes/{nid}", headers=h, json={"body": "Updated"}
    )
    assert patched.status_code == 200
    assert patched.json()["body"] == "Updated"

    deleted = auth_client.delete(f"/contacts/{cid}/notes/{nid}", headers=h)
    assert deleted.status_code == 204

    missing = auth_client.get(f"/contacts/{cid}/notes/{nid}", headers=h)
    assert missing.status_code == 404


def test_notes_on_other_users_contact_return_404(auth_client: TestClient) -> None:
    ta = _register_token(auth_client, "alice@example.com", "a")
    tb = _register_token(auth_client, "bob@example.com", "b")
    c = auth_client.post(
        "/contacts",
        headers=_bearer(ta),
        json={"name": "Alice only"},
    )
    assert c.status_code == 201
    cid = c.json()["id"]
    n = auth_client.post(
        f"/contacts/{cid}/notes",
        headers=_bearer(ta),
        json={"body": "secret"},
    )
    assert n.status_code == 201
    nid = n.json()["id"]

    hb = _bearer(tb)
    assert auth_client.get(f"/contacts/{cid}/notes", headers=hb).status_code == 404
    assert (
        auth_client.post(
            f"/contacts/{cid}/notes", headers=hb, json={"body": "nope"}
        ).status_code
        == 404
    )
    assert (
        auth_client.get(f"/contacts/{cid}/notes/{nid}", headers=hb).status_code == 404
    )
    assert (
        auth_client.patch(
            f"/contacts/{cid}/notes/{nid}", headers=hb, json={"body": "hack"}
        ).status_code
        == 404
    )
    assert (
        auth_client.delete(f"/contacts/{cid}/notes/{nid}", headers=hb).status_code
        == 404
    )

    still = auth_client.get(f"/contacts/{cid}/notes/{nid}", headers=_bearer(ta))
    assert still.status_code == 200


def test_note_create_with_interaction_and_occurred_at(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "notes@example.com", "secret123")
    h = _bearer(token)
    cid = auth_client.post("/contacts", headers=h, json={"name": "C"}).json()["id"]
    r = auth_client.post(
        f"/contacts/{cid}/notes",
        headers=h,
        json={
            "body": "Discussed pricing",
            "interaction_type": "call",
            "occurred_at": "2026-03-20T15:30:00+00:00",
        },
    )
    assert r.status_code == 201
    row = r.json()
    assert row["body"] == "Discussed pricing"
    assert row["interaction_type"] == "call"
    assert row["occurred_at"] is not None


def test_note_invalid_interaction_type_422(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "itype@example.com", "secret123")
    h = _bearer(token)
    cid = auth_client.post("/contacts", headers=h, json={"name": "C"}).json()["id"]
    r = auth_client.post(
        f"/contacts/{cid}/notes",
        headers=h,
        json={"body": "x", "interaction_type": "telepathy"},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"


def test_note_occurred_at_naive_datetime_422(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "naive@example.com", "secret123")
    h = _bearer(token)
    cid = auth_client.post("/contacts", headers=h, json={"name": "C"}).json()["id"]
    r = auth_client.post(
        f"/contacts/{cid}/notes",
        headers=h,
        json={"body": "x", "occurred_at": "2026-03-20T15:30:00"},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"


def test_note_patch_clears_interaction_and_occurred_at(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "clear@example.com", "secret123")
    h = _bearer(token)
    cid = auth_client.post("/contacts", headers=h, json={"name": "C"}).json()["id"]
    n = auth_client.post(
        f"/contacts/{cid}/notes",
        headers=h,
        json={
            "body": "x",
            "interaction_type": "meeting",
            "occurred_at": "2026-01-01T00:00:00+00:00",
        },
    )
    nid = n.json()["id"]
    r = auth_client.patch(
        f"/contacts/{cid}/notes/{nid}",
        headers=h,
        json={"interaction_type": None, "occurred_at": None},
    )
    assert r.status_code == 200
    row = r.json()
    assert row["interaction_type"] is None
    assert row["occurred_at"] is None


def test_note_patch_body_null_422(auth_client: TestClient) -> None:
    token = _register_token(auth_client, "bnull@example.com", "secret123")
    h = _bearer(token)
    cid = auth_client.post("/contacts", headers=h, json={"name": "C"}).json()["id"]
    nid = auth_client.post(
        f"/contacts/{cid}/notes", headers=h, json={"body": "x"}
    ).json()["id"]
    r = auth_client.patch(
        f"/contacts/{cid}/notes/{nid}", headers=h, json={"body": None}
    )
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "validation_error"
    assert "null" in body["message"].lower()
