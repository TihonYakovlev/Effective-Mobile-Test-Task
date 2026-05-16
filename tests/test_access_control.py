import pytest

from apps.access.models import AccessRule


@pytest.mark.django_db
def test_resource_endpoint_requires_authentication(api_client, demo_data):
    response = api_client.get("/api/resources/orders/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication credentials were not provided"


@pytest.mark.django_db
def test_regular_user_sees_only_own_orders_and_cannot_read_rules(
    authenticated_client,
):
    client = authenticated_client("user@example.com", "user12345")

    list_response = client.get("/api/resources/orders/")
    own_order_response = client.get("/api/resources/orders/1/")
    foreign_order_response = client.get("/api/resources/orders/2/")
    access_rules_response = client.get("/api/access/rules/")

    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "id": 1,
            "title": "First order",
            "owner_email": "user@example.com",
        }
    ]
    assert own_order_response.status_code == 200
    assert foreign_order_response.status_code == 403
    assert access_rules_response.status_code == 403


@pytest.mark.django_db
def test_manager_reads_all_orders_but_still_cannot_manage_access_rules(
    authenticated_client,
):
    client = authenticated_client("manager@example.com", "manager12345")

    orders_response = client.get("/api/resources/orders/")
    access_rules_response = client.get("/api/access/rules/")

    assert orders_response.status_code == 200
    assert [order["id"] for order in orders_response.json()] == [1, 2]
    assert access_rules_response.status_code == 403


@pytest.mark.django_db
def test_admin_can_read_and_update_access_rules(authenticated_client):
    client = authenticated_client("admin@example.com", "admin12345")
    rule = AccessRule.objects.get(role__code="user", element__code="products")

    list_response = client.get("/api/access/rules/")
    update_response = client.patch(
        f"/api/access/rules/{rule.id}/",
        {"create_permission": True},
        format="json",
    )

    rule.refresh_from_db()

    assert list_response.status_code == 200
    assert update_response.status_code == 200
    assert rule.create_permission is True
