"""API error envelope (PIN-009): stable JSON keys for client mistakes."""

from fastapi.testclient import TestClient


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_validation_error_shape_on_register(auth_client: TestClient) -> None:
    r = auth_client.post(
        "/auth/register", json={"email": "not-an-email", "password": "x"}
    )
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "validation_error"
    assert body["message"] == "Request validation failed"
    assert isinstance(body["details"], list)
    assert len(body["details"]) >= 1
    assert "type" in body["details"][0]
    assert "loc" in body["details"][0]


def test_unauthorized_shape_without_bearer(auth_client: TestClient) -> None:
    r = auth_client.get("/contacts")
    assert r.status_code == 401
    body = r.json()
    assert body["error"] == "unauthorized"
    assert body["message"] == "Not authenticated"
    assert "detail" not in body
    assert r.headers.get("www-authenticate", "").lower().startswith("bearer")


def test_not_found_shape_for_missing_contact(auth_client: TestClient) -> None:
    reg = auth_client.post(
        "/auth/register",
        json={"email": "u@example.com", "password": "secret123"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    r = auth_client.get("/contacts/99999", headers=_bearer(token))
    assert r.status_code == 404
    body = r.json()
    assert body["error"] == "not_found"
    assert body["message"] == "Contact not found"
    assert "detail" not in body


def test_conflict_shape_on_duplicate_register(auth_client: TestClient) -> None:
    body = {"email": "dup@example.com", "password": "p1"}
    assert auth_client.post("/auth/register", json=body).status_code == 201
    r2 = auth_client.post("/auth/register", json=body)
    assert r2.status_code == 409
    out = r2.json()
    assert out["error"] == "conflict"
    assert out["message"] == "Email already registered"
    assert "detail" not in out


def test_login_failure_is_401_not_500(auth_client: TestClient) -> None:
    auth_client.post(
        "/auth/register",
        json={"email": "only@example.com", "password": "right"},
    )
    r = auth_client.post(
        "/auth/login",
        json={"email": "only@example.com", "password": "wrong-pass"},
    )
    assert r.status_code == 401
    assert r.json()["error"] == "unauthorized"
    assert "traceback" not in r.text.lower()
