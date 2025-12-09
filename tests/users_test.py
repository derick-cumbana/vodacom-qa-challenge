import pytest
import requests
import uuid

BASE_URL = "http://localhost:80"

@pytest.fixture
def token():
    payload = {
        "grant_type": "password",
        "username": "user",
        "password": "pass123"
    }
    response = requests.post(BASE_URL + "/token", data=payload)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_users_with_valid_token(auth_header):
    response = requests.get(f"{BASE_URL}/users/", headers=auth_header)
    assert response.status_code == 200

    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0

    first_user = users[0]
    assert "username" in first_user
    assert "email" in first_user
    assert "full_name" in first_user
    assert "disabled" in first_user
    assert "created_at" in first_user
    assert "id" in first_user

def test_get_users_with_no_token():
    response = requests.get(f"{BASE_URL}/users/")
    assert response.status_code == 401

def test_get_users_invalid_token():
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    assert response.status_code == 401

def generate_random_email():
    return f"user_{uuid.uuid4().hex[:8]}@example.com"

def generate_random_username():
    return f"user_{uuid.uuid4().hex[:8]}"

def test_create_user_with_valid_input(auth_header):
    email = generate_random_email()
    username = generate_random_username()

    payload = {
        "email": email,
        "username": username,
        "full_name": "New User",
        "disabled": True,
        "password": "StrongPass123"
    }

    headers = {**auth_header, "Content-Type": "application/json"}

    response = requests.post(f"{BASE_URL}/users/", headers=headers, json=payload)

    assert response.status_code == 201
    user = response.json()

    assert user["email"] == payload["email"]
    assert user["username"] == payload["username"]
    assert user["full_name"] == payload["full_name"]
    assert str(user["disabled"]) == str(payload["disabled"])
    assert "id" in user
    assert "created_at" in user


def get_first_user(auth_header):
    headers = auth_header
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    response.raise_for_status()
    users = response.json()
    if not users:
        raise ValueError("No users found in /users/")
    return users[0]

def test_create_user_with_existing_email_and_username(auth_header):
    existing_user = get_first_user(auth_header)

    payload = {
        "email": existing_user["email"],
        "username": existing_user["username"],
        "full_name": "Duplicate User",
        "disabled": False,
        "password": "StrongPass123"
    }

    headers = {**auth_header, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/users/", headers=headers, json=payload)

    assert response.status_code == 409, "API should reject duplicate email/username"

def test_create_user_invalid_disabled_field_data_type(auth_header):

    payload = {
        "email": generate_random_email(),
        "username": generate_random_username(),
        "full_name": "Invalid Disabled",
        "disabled": "not_a_boolean",
        "password": "StrongPass123"
    }

    headers = {**auth_header, "Content-Type": "application/json"}

    response = requests.post(f"{BASE_URL}/users/", headers=headers, json=payload)

    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json


