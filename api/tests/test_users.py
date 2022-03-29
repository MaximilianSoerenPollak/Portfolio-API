from jose import jwt
from api import schemas
from api.config import settings
import pytest


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
