from .conftest import register_and_login


def test_register_returns_user_without_password(client):
    resp = client.post("/api/auth/register", json={"email": "a@example.com", "password": "pw123"})

    assert resp.status_code == 201
    assert resp.json()["email"] == "a@example.com"
    assert "hashed_password" not in resp.json()


def test_register_rejects_duplicate_email(client):
    client.post("/api/auth/register", json={"email": "a@example.com", "password": "pw123"})
    resp = client.post("/api/auth/register", json={"email": "a@example.com", "password": "other"})

    assert resp.status_code == 400


def test_register_rejects_password_with_spaces(client):
    resp = client.post("/api/auth/register", json={"email": "a@example.com", "password": "pw 123"})

    assert resp.status_code == 422


def test_login_with_wrong_password_is_unauthorized(client):
    client.post("/api/auth/register", json={"email": "a@example.com", "password": "pw123"})
    resp = client.post("/api/auth/login", data={"username": "a@example.com", "password": "nope"})

    assert resp.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/me").status_code == 401


def test_me_returns_current_user(client):
    headers = register_and_login(client, email="me@example.com")

    assert client.get("/api/me", headers=headers).json()["email"] == "me@example.com"


def test_invalid_token_is_rejected(client):
    assert client.get("/api/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
