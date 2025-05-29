from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "fullname": "Test User",
        "gender": "other"
    })
    assert response.status_code == 200 or response.status_code == 400  # Có thể trùng email/username
    if response.status_code == 200:
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"

def test_login_user():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "testuser"
