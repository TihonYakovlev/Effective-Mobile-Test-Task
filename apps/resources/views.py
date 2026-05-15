from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.access.permissions import require_access
from apps.resources.mock_data import MOCK_ORDERS, MOCK_PRODUCTS


def get_mock_object(objects: list[dict], pk: int) -> dict:
    for item in objects:
        if item["id"] == pk:
            return item
    raise NotFound("Resource not found")


def ensure_object_access(request, item: dict, element_code: str, action: str):
    decision = require_access(request, element_code, action)

    if decision.can_access_all:
        return decision

    if item["owner_email"] == request.user.email:
        return decision

    raise PermissionDenied("You can access only your own resources")


class OrdersView(APIView):
    def get(self, request):
        decision = require_access(request, "orders", "read")

        if decision.can_access_all:
            return Response(MOCK_ORDERS)

        own_orders = [
            order for order in MOCK_ORDERS
            if order["owner_email"] == request.user.email
        ]
        return Response(own_orders)

    def post(self, request):
        require_access(request, "orders", "create")
        return Response(
            {"message": "Order creation is allowed by access rules"},
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    def get(self, request, pk: int):
        order = get_mock_object(MOCK_ORDERS, pk)
        ensure_object_access(request, order, "orders", "read")
        return Response(order)

    def patch(self, request, pk: int):
        order = get_mock_object(MOCK_ORDERS, pk)
        ensure_object_access(request, order, "orders", "update")
        return Response(
            {
                "message": "Order update is allowed by access rules",
                "order": order,
            }
        )

    def delete(self, request, pk: int):
        order = get_mock_object(MOCK_ORDERS, pk)
        ensure_object_access(request, order, "orders", "delete")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductsView(APIView):
    def get(self, request):
        decision = require_access(request, "products", "read")

        if decision.can_access_all:
            return Response(MOCK_PRODUCTS)

        own_products = [
            product for product in MOCK_PRODUCTS
            if product["owner_email"] == request.user.email
        ]
        return Response(own_products)

    def post(self, request):
        require_access(request, "products", "create")
        return Response(
            {"message": "Product creation is allowed by access rules"},
            status=status.HTTP_201_CREATED,
        )
