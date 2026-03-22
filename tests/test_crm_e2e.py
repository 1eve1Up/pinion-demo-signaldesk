"""End-to-end SignalDesk CRM API scenario (sprint demo).

``test_crm_happy_path_full_story`` walks the intended product slice:

1. Register a user and obtain a JWT (bearer).
2. Create two contacts, list them, fetch one by id, rename it with PATCH.
3. On one contact, create two notes, list them, GET one, PATCH one, DELETE one.
4. DELETE the contact (child notes are removed via cascade).
5. Log in with the same email/password and verify the contact list is empty.

Other tests in this module cover representative failures (401 without auth,
404 across users, bogus bearer) without depending on test order; each uses
``auth_client``, which provisions a fresh SQLite database per test function.
"""

from fastapi.testclient import TestClient


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_crm_happy_path_full_story(auth_client: TestClient) -> None:
    reg = auth_client.post(
        "/auth/register",
        json={"email": "rep@example.com", "password": "register-secret-1"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    h = _bearer(token)

    c1 = auth_client.post("/contacts", headers=h, json={"name": "Northwind"})
    c2 = auth_client.post("/contacts", headers=h, json={"name": "Contoso"})
    assert c1.status_code == 201
    assert c2.status_code == 201
    id1, id2 = c1.json()["id"], c2.json()["id"]

    listed = auth_client.get("/contacts", headers=h)
    assert listed.status_code == 200
    assert {row["name"] for row in listed.json()} == {"Northwind", "Contoso"}

    one = auth_client.get(f"/contacts/{id1}", headers=h)
    assert one.status_code == 200
    assert one.json()["name"] == "Northwind"

    patched = auth_client.patch(
        f"/contacts/{id1}", headers=h, json={"name": "Northwind Ltd"}
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Northwind Ltd"

    n_a = auth_client.post(
        f"/contacts/{id1}/notes", headers=h, json={"body": "Called - interested"}
    )
    n_b = auth_client.post(
        f"/contacts/{id1}/notes", headers=h, json={"body": "Sent follow-up deck"}
    )
    assert n_a.status_code == 201
    assert n_b.status_code == 201
    na_id, nb_id = n_a.json()["id"], n_b.json()["id"]

    notes = auth_client.get(f"/contacts/{id1}/notes", headers=h)
    assert notes.status_code == 200
    assert len(notes.json()) == 2

    g = auth_client.get(f"/contacts/{id1}/notes/{na_id}", headers=h)
    assert g.status_code == 200
    assert "interested" in g.json()["body"]

    upd = auth_client.patch(
        f"/contacts/{id1}/notes/{na_id}",
        headers=h,
        json={"body": "Called - very interested"},
    )
    assert upd.status_code == 200
    assert upd.json()["body"] == "Called - very interested"

    dnote = auth_client.delete(f"/contacts/{id1}/notes/{nb_id}", headers=h)
    assert dnote.status_code == 204

    left = auth_client.get(f"/contacts/{id1}/notes", headers=h)
    assert left.status_code == 200
    assert len(left.json()) == 1

    dc = auth_client.delete(f"/contacts/{id1}", headers=h)
    assert dc.status_code == 204

    still_other = auth_client.get(f"/contacts/{id2}", headers=h)
    assert still_other.status_code == 200

    login = auth_client.post(
        "/auth/login",
        json={"email": "rep@example.com", "password": "register-secret-1"},
    )
    assert login.status_code == 200
    h2 = _bearer(login.json()["access_token"])
    final_list = auth_client.get("/contacts", headers=h2)
    assert final_list.status_code == 200
    assert len(final_list.json()) == 1
    assert final_list.json()[0]["name"] == "Contoso"


def test_crm_protected_routes_require_valid_bearer(auth_client: TestClient) -> None:
    auth_client.post(
        "/auth/register",
        json={"email": "solo@example.com", "password": "p"},
    )
    c = auth_client.post("/contacts", json={"name": "X"})
    assert c.status_code == 401

    bad = auth_client.get(
        "/contacts",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert bad.status_code == 401


def test_crm_cross_user_contact_and_notes_stay_private(auth_client: TestClient) -> None:
    ta = auth_client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "a"},
    ).json()["access_token"]
    tb = auth_client.post(
        "/auth/register",
        json={"email": "b@example.com", "password": "b"},
    ).json()["access_token"]
    ha, hb = _bearer(ta), _bearer(tb)

    cid = auth_client.post("/contacts", headers=ha, json={"name": "A-only"}).json()[
        "id"
    ]
    nid = auth_client.post(
        f"/contacts/{cid}/notes",
        headers=ha,
        json={"body": "secret"},
    ).json()["id"]

    assert auth_client.get(f"/contacts/{cid}", headers=hb).status_code == 404
    assert auth_client.get(f"/contacts/{cid}/notes", headers=hb).status_code == 404
    assert (
        auth_client.get(f"/contacts/{cid}/notes/{nid}", headers=hb).status_code == 404
    )
