from rest_framework.routers import DefaultRouter

from apps.access.admin_api import AccessRuleViewSet, BusinessElementViewSet, RoleViewSet


router = DefaultRouter()
router.register("access/roles", RoleViewSet, basename="roles")
router.register("access/elements", BusinessElementViewSet, basename="elements")
router.register("access/rules", AccessRuleViewSet, basename="access-rules")

urlpatterns = router.urls