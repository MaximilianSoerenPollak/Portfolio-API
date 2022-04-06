from jose import jwt
from api import schemas
from api.config import settings
import pytest
from datetime import datetime


def test_create_user(client):
    res = client.post("/users/", json={"email": "test@test.com", "password": "password123"})
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == "test@test.com"
    assert res.status_code == 201


def test_login_user(client, test_user):
    res = client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
    id_ = payload.get("user_id")
    assert id_ == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrong_email@testmail.com", "password123", 403),
        ("test@test.com", "wrong_password123", 403),
        ("wrong_email@email.com", "wrong_password123", 403),
        (None, "wrong_password123", 422),
        ("wrong_email@testmail.com", None, 422),
        (None, None, 422),
    ],
)
def test_incorrect_login(client, test_user, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code


def test_check_get_single_user(client, test_user):
    res = client.get(f"/{test_user['id']}")
    print(res.json())
    response = schemas.UserResponse(**res.json())
    assert res.status_code == 200


def test_user_deletion(authorized_client):
    res = authorized_client.delete("/delete")
    assert res.status_code == 204


def test_check_user_deletion(authorized_client, test_user):
    res = authorized_client.get(f"/{test_user['id']}/")
    assert res.status_code == 404


def test_test(client):
    res = client.get("/1")
    assert res.status_code == 200
