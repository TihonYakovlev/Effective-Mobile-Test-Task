from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from apps.access.services import check_access


def require_access(request, element_code: str, action: str):
    if request.user is None:
        raise NotAuthenticated("Authentication credentials were not provided")

    decision = check_access(request.user, element_code, action)
    if not decision.allowed:
        raise PermissionDenied("You do not have permission to access this resource")

    return decision