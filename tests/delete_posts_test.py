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
    response = requests.post(f"{BASE_URL}/token", data=payload)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def generate_random_string(length=8):
    return uuid.uuid4().hex[:length]

def generate_post_payload(title=None, content=None, public=True):
    return {
        "title": title or f"Title {generate_random_string()}",
        "content": content or f"Content {generate_random_string()}",
        "public": public
    }

def create_user_and_get_auth():
    username = f"user_{generate_random_string()}"
    email = f"{username}@example.com"
    password = "TestPass123"

    payload = {
        "username": username,
        "email": email,
        "full_name": "Test User",
        "disabled": False,
        "password": password
    }
    resp = requests.post(f"{BASE_URL}/users/", json=payload, headers={"Content-Type": "application/json"})
    assert resp.status_code == 201, f"Failed to create user: {resp.text}"

    auth_payload = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    auth_resp = requests.post(f"{BASE_URL}/token", data=auth_payload)
    assert auth_resp.status_code == 200, f"Failed to authenticate user: {auth_resp.text}"
    token = auth_resp.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

def test_delete_own_post(auth_header):
    headers = {**auth_header, "Content-Type": "application/json"}
    payload = generate_post_payload()
    create_resp = requests.post(f"{BASE_URL}/posts/", headers=headers, json=payload)
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]


    delete_resp = requests.delete(f"{BASE_URL}/posts/{post_id}", headers=headers)
    assert delete_resp.status_code == 204, f"Owner should be able to delete their post: {delete_resp.text}"

def test_delete_post_by_another_user(auth_header):

    headers = {**auth_header, "Content-Type": "application/json"}
    payload = generate_post_payload()
    create_resp = requests.post(f"{BASE_URL}/posts/", headers=headers, json=payload)
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    other_auth = create_user_and_get_auth()
    headers_other = {**other_auth, "Content-Type": "application/json"}

    delete_resp = requests.delete(f"{BASE_URL}/posts/{post_id}", headers=headers_other)
    assert delete_resp.status_code == 403, f"New user should not delete post {post_id} of another user: {delete_resp.text}"
