from django.urls import path

from apps.resources.views import OrderDetailView, OrdersView, ProductsView


urlpatterns = [
    path("resources/orders/", OrdersView.as_view(), name="orders"),
    path("resources/orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("resources/products/", ProductsView.as_view(), name="products"),
]