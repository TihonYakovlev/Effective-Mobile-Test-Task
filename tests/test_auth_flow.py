import pytest

from apps.access.models import UserRole
from apps.users.models import AuthSession, User
from apps.users.passwords import check_password


@pytest.mark.django_db
def test_register_login_and_logout_revoke_current_token(api_client):
    raw_password = "strongpass123"

    register_response = api_client.post(
        "/api/auth/register/",
        {
            "email": "New.User@Example.com",
            "first_name": "New",
            "last_name": "User",
            "middle_name": "",
            "password": raw_password,
            "password_repeat": raw_password,
        },
        format="json",
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "new.user@example.com"
    assert "password" not in register_response.json()

    user = User.objects.get(email="new.user@example.com")
    assert user.password_hash != raw_password
    assert check_password(raw_password, user.password_hash)
    assert UserRole.objects.filter(user=user, role__code="user").exists()

    login_response = api_client.post(
        "/api/auth/login/",
        {"email": user.email, "password": raw_password},
        format="json",
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert AuthSession.objects.filter(user=user, revoked_at__isnull=True).exists()

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    me_response = api_client.get("/api/users/me/")

    assert me_response.status_code == 200
    assert me_response.json()["email"] == user.email

    logout_response = api_client.post("/api/auth/logout/")

    assert logout_response.status_code == 204

    revoked_response = api_client.get("/api/users/me/")

    assert revoked_response.status_code == 401
    assert revoked_response.json()["detail"] == "Session revoked"


@pytest.mark.django_db
def test_soft_delete_deactivates_account_and_blocks_future_login(api_client):
    password = "deletepass123"
    api_client.post(
        "/api/auth/register/",
        {
            "email": "delete.me@example.com",
            "first_name": "Delete",
            "last_name": "Me",
            "middle_name": "",
            "password": password,
            "password_repeat": password,
        },
        format="json",
    )

    login_response = api_client.post(
        "/api/auth/login/",
        {"email": "delete.me@example.com", "password": password},
        format="json",
    )
    token = login_response.json()["access_token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    delete_response = api_client.delete("/api/users/me/")

    assert delete_response.status_code == 204

    user = User.objects.get(email="delete.me@example.com")
    assert user.is_active is False
    assert user.deleted_at is not None
    assert not AuthSession.objects.filter(user=user, revoked_at__isnull=True).exists()

    api_client.credentials()
    second_login_response = api_client.post(
        "/api/auth/login/",
        {"email": "delete.me@example.com", "password": password},
        format="json",
    )

    assert second_login_response.status_code == 401

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    old_token_response = api_client.get("/api/users/me/")

    assert old_token_response.status_code == 401
