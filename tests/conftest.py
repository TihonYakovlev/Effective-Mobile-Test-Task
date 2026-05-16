import pytest
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def demo_data(db):
    call_command("seed_demo_data", verbosity=0)


@pytest.fixture
def authenticated_client(demo_data):
    def login(email: str, password: str) -> APIClient:
        client = APIClient()
        response = client.post(
            "/api/auth/login/",
            {"email": email, "password": password},
            format="json",
        )
        assert response.status_code == 200

        token = response.json()["access_token"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    return login
