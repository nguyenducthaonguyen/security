import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Thông tin người dùng test đã có sẵn trong DB (hoặc bạn tạo trước bằng register)
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"

@pytest.fixture(scope="module")
def get_token():
    response = client.post("/api/v1/auth/login", data={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return f"Bearer {token}"


def test_get_current_user_info(get_token):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": get_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USERNAME
    assert "email" in data


def test_update_current_user_info(get_token):
    payload = {
        "email": "Nguyen214243@gmail.com",
        "fullname": "Updated Name",
        "gender": "male"
    }
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": get_token},
        json=payload
    )
    assert response.status_code == 200
    assert response.json()["fullname"] == "Updated Name"
