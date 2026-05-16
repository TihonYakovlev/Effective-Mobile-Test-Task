from dataclasses import dataclass

from apps.access.models import AccessRule
from apps.users.models import User


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    can_access_all: bool = False


ACTION_TO_FIELDS = {
    "read": ("read_permission", "read_all_permission"),
    "create": ("create_permission", None),
    "update": ("update_permission", "update_all_permission"),
    "delete": ("delete_permission", "delete_all_permission"),
}


def check_access(user: User, element_code: str, action: str) -> AccessDecision:
    own_field, all_field = ACTION_TO_FIELDS[action]

    rules = AccessRule.objects.filter(
        role__user_links__user=user,
        element__code=element_code,
    )

    can_access_all = False
    can_access_own = False

    for rule in rules:
        if all_field and getattr(rule, all_field):
            can_access_all = True
        if getattr(rule, own_field):
            can_access_own = True

    return AccessDecision(
        allowed=can_access_all or can_access_own,
        can_access_all=can_access_all,
    )