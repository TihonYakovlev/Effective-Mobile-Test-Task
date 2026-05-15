from rest_framework import viewsets

from apps.access.models import AccessRule, BusinessElement, Role
from apps.access.permissions import require_access
from apps.access.serializers import (
    AccessRuleSerializer,
    BusinessElementSerializer,
    RoleSerializer,
)


class AdminAccessMixin:
    element_code = "access_rules"

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        action = "read" if request.method == "GET" else "update"
        require_access(request, self.element_code, action)


class RoleViewSet(AdminAccessMixin, viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class BusinessElementViewSet(AdminAccessMixin, viewsets.ModelViewSet):
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer


class AccessRuleViewSet(AdminAccessMixin, viewsets.ModelViewSet):
    queryset = AccessRule.objects.select_related("role", "element")
    serializer_class = AccessRuleSerializer