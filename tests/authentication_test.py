import uuid
import requests

BASE_URL = "http://localhost:80/"

def test_authentication_with_valid_credentials():
    payload = {
        "username": "user",
        "password": "pass123",
    }

    response = requests.post(BASE_URL + "/token", data=payload)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "bearer" == response.json()["token_type"]

def test_authentication_with_invalid_password():
    payload = {
        "username": "user",
        "password": "wrongpass",
    }

    response = requests.post(BASE_URL + "/token", data=payload)

    assert response.status_code == 401
    assert "access_token" not in response.json()

def test_authentication_with_missing_fields():
    payload = { "username": "user" }

    response = requests.post(BASE_URL + "/token", data=payload)

    assert response.status_code == 422
    assert "access_token" not in response.json()

def generate_random_string(length=8):
    return uuid.uuid4().hex[:length]

def create_disabled_user():

    username = f"user_{generate_random_string()}"
    email = f"{username}@example.com"
    password = "TestPass123"

    payload = {
        "username": username,
        "email": email,
        "full_name": "Disabled User",
        "disabled": True,
        "password": password
    }

    resp = requests.post(f"{BASE_URL}/users/", json=payload, headers={"Content-Type": "application/json"})
    assert resp.status_code == 201, f"Failed to create disabled user: {resp.text}"
    return username, password

def test_authentication_disabled_user():
    username, password = create_disabled_user()

    payload = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    response = requests.post(f"{BASE_URL}/token", data=payload)

    assert response.status_code == 401, f"Disabled user should not authenticate: {response.text}"
    assert "access_token" not in response.json()