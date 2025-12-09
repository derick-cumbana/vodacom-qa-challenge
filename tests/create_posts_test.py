import requests
import uuid
import pytest
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

def test_create_post_valid(auth_header):
    payload = generate_post_payload()
    headers = {**auth_header, "Content-Type": "application/json"}

    response = requests.post(f"{BASE_URL}/posts/", headers=headers, json=payload)
    assert response.status_code == 201

    post = response.json()
    assert_post_response(post, payload)

def assert_post_response(post, payload):
    assert post["title"] == payload["title"]
    assert post["content"] == payload["content"]

    post_public = post["public"]
    if isinstance(post_public, str):
        post_public = post_public.lower() == "true"
    assert post_public == payload["public"]


    for field in ["id", "created_at", "owner_id"]:
        assert field in post


@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"content": "Content only", "public": True}, "Post should not be created without a title"),
        ({"title": "Title only", "public": True}, "Post should not be created without content"),
        ({"title": "Title", "content": "Content"}, "Post should not be created without public field")
    ]
)
def test_create_post_with_missing_fields(auth_header, payload, expected_message):
    headers = {**auth_header, "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/posts/", headers=headers, json=payload)
    assert response.status_code == 422, expected_message


def test_create_posts_same_title_content(auth_header):
    payload = generate_post_payload(title="DuplicateTitle", content="DuplicateContent")
    headers = {**auth_header, "Content-Type": "application/json"}

    response1 = requests.post(f"{BASE_URL}/posts/", headers=headers, json=payload)
    assert response1.status_code == 201

    response2 = requests.post(f"{BASE_URL}/posts/", headers=headers, json=payload)
    assert response2.status_code == 409, "It should return 409 Conflict to avoid generating many equal posts"

def test_create_post_public_and_private(auth_header):
    for is_public in [True, False]:
        payload = generate_post_payload(public=is_public)
        headers = {**auth_header, "Content-Type": "application/json"}
        response = requests.post(f"{BASE_URL}/posts/", headers=headers, json=payload)
        assert response.status_code == 201
        post = response.json()
        post_public = post["public"]
        if isinstance(post_public, str):
            post_public = post_public.lower() == "true"
        assert post_public == is_public



