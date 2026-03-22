from fastapi.testclient import TestClient

from signaldesk.security import decode_access_token


def test_register_then_login_returns_bearer_token(auth_client: TestClient) -> None:
    email = "newuser@example.com"
    password = "safe-password-xyz"
    reg = auth_client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert reg.status_code == 201
    reg_body = reg.json()
    assert reg_body["token_type"] == "bearer"
    assert reg_body["access_token"]
    payload = decode_access_token(reg_body["access_token"])
    assert payload["sub"].isdigit()

    login = auth_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    login_body = login.json()
    assert login_body["token_type"] == "bearer"
    assert login_body["access_token"]


def test_register_duplicate_email_returns_409(auth_client: TestClient) -> None:
    body = {"email": "dup@example.com", "password": "p1"}
    r1 = auth_client.post("/auth/register", json=body)
    assert r1.status_code == 201
    r2 = auth_client.post("/auth/register", json=body)
    assert r2.status_code == 409


def test_login_wrong_password_returns_401(auth_client: TestClient) -> None:
    auth_client.post(
        "/auth/register",
        json={"email": "u@example.com", "password": "right-pass"},
    )
    bad = auth_client.post(
        "/auth/login",
        json={"email": "u@example.com", "password": "wrong-pass"},
    )
    assert bad.status_code == 401
    assert "access_token" not in bad.json()


def test_openapi_lists_auth_routes(auth_client: TestClient) -> None:
    spec = auth_client.get("/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    assert "/auth/register" in paths
    assert "/auth/login" in paths
