from backend.app.core.security import hash_password, verify_password

def test_password_hashing():
    pwd = "superSecretPassword123!"
    hashed, salt = hash_password(pwd)
    assert hashed != pwd
    assert len(salt) > 0
    assert verify_password(pwd, hashed, salt) is True
    assert verify_password("wrongPassword", hashed, salt) is False

def test_login_success(client):
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["username"] == "admin"

def test_login_failure(client):
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "admin", "password": "wrong_password"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"

def test_current_user_me(client):
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": "admin", "password": "admin123"}
    )
    token = login_res.json()["token"]

    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "admin"

def test_unauthorized_access(client):
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 401
    assert me_res.json()["error"]["code"] == "UNAUTHORIZED"
