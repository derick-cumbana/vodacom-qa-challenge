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


def generate_random_string(length=8):
    return uuid.uuid4().hex[:length]

def generate_post_payload(title=None, content=None, public=True):
    return {
        "title": title or f"Title {generate_random_string()}",
        "content": content or f"Content {generate_random_string()}",
        "public": public
    }

def assert_post_response(post, payload):
    assert post["title"] == payload["title"]
    assert post["content"] == payload["content"]
    post_public = post["public"]
    if isinstance(post_public, str):
        post_public = post_public.lower() == "true"
    assert post_public == payload["public"]
    for field in ["id", "created_at", "owner_id"]:
        assert field in post

def test_update_post_by_owner(auth_header):
    headers = {**auth_header, "Content-Type": "application/json"}

    payload = generate_post_payload()
    create_resp = requests.post(f"{BASE_URL}/posts/", headers=headers, json=payload)
    assert create_resp.status_code == 201
    post = create_resp.json()
    post_id = post["id"]

    updated_payload = generate_post_payload()
    update_resp = requests.put(f"{BASE_URL}/posts/{post_id}", headers=headers, json=updated_payload)
    assert update_resp.status_code == 200
    updated_post = update_resp.json()
    assert_post_response(updated_post, updated_payload)


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

def test_update_another_users_post_with_new_ser():

    auth_header = create_user_and_get_auth()
    headers = {**auth_header, "Content-Type": "application/json"}

    updated_payload = generate_post_payload()
    update_resp = requests.put(f"{BASE_URL}/posts/1", headers=headers, json=updated_payload)

    assert update_resp.status_code ==403, f"New user should not update post 1 of another user: {update_resp.text}"

