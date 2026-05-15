from django.core.management.base import BaseCommand
from django.db import transaction

from apps.access.models import AccessRule, BusinessElement, Role, UserRole
from apps.users.models import User
from apps.users.passwords import hash_password


class Command(BaseCommand):
    help = "Create demo users, roles, business elements and access rules."

    @transaction.atomic
    def handle(self, *args, **options):
        roles = self._create_roles()
        elements = self._create_business_elements()
        users = self._create_users()
        self._assign_roles(users, roles)
        self._create_access_rules(roles, elements)

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))

    def _create_roles(self) -> dict[str, Role]:
        role_data = {
            "admin": {
                "name": "Admin",
                "description": "Can manage users, resources and access rules",
            },
            "manager": {
                "name": "Manager",
                "description": "Can manage business resources",
            },
            "user": {
                "name": "User",
                "description": "Default registered userr",
            },
        }

        roles = {}
        for code, data in role_data.items():
            role, _ = Role.objects.update_or_create(
                code=code,
                defaults=data,
            )
            roles[code] = role

        return roles

    def _create_business_elements(self) -> dict[str, BusinessElement]:
        element_data = {
            "users": {
                "name": "Users",
                "description": "User accounts and profiles.",
            },
            "orders": {
                "name": "Orders",
                "description": "Mock customer orders.",
            },
            "products": {
                "name": "Products",
                "description": "Mock product catalog.",
            },
            "access_rules": {
                "name": "Access rules",
                "description": "Roles, resources and permission rules.",
            },
        }

        elements = {}
        for code, data in element_data.items():
            element, _ = BusinessElement.objects.update_or_create(
                code=code,
                defaults=data,
            )
            elements[code] = element

        return elements

    def _create_users(self) -> dict[str, User]:
        user_data = {
            "admin": {
                "email": "admin@myemail.com",
                "first_name": "Admin",
                "last_name": "User",
                "password": "admin12345",
            },
            "manager": {
                "email": "manager@myemail.com",
                "first_name": "Manager",
                "last_name": "User",
                "password": "manager12345",
            },
            "user": {
                "email": "user@myemail.com",
                "first_name": "Regular",
                "last_name": "User",
                "password": "user12345",
            },
        }

        users = {}
        for code, data in user_data.items():
            password = data.pop("password")
            user, _ = User.objects.update_or_create(
                email=data["email"],
                defaults={
                    **data,
                    "middle_name": "",
                    "password_hash": hash_password(password),
                    "is_active": True,
                    "deleted_at": None,
                },
            )
            users[code] = user

        return users

    def _assign_roles(
        self,
        users: dict[str, User],
        roles: dict[str, Role],
    ) -> None:
        assignments = {
            "admin": "admin",
            "manager": "manager",
            "user": "user",
        }

        for user_code, role_code in assignments.items():
            UserRole.objects.get_or_create(
                user=users[user_code],
                role=roles[role_code],
            )

    def _create_access_rules(
        self,
        roles: dict[str, Role],
        elements: dict[str, BusinessElement],
    ) -> None:
        rules = {
            "admin": {
                "users": {
                    "read_all_permission": True,
                    "update_all_permission": True,
                    "delete_all_permission": True,
                },
                "orders": {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                    "delete_all_permission": True,
                },
                "products": {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                    "delete_all_permission": True,
                },
                "access_rules": {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                    "delete_all_permission": True,
                },
            },
            "manager": {
                "orders": {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                },
                "products": {
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_all_permission": True,
                },
            },
            "user": {
                "orders": {
                    "read_permission": True,
                    "create_permission": True,
                    "update_permission": True,
                    "delete_permission": True,
                },
                "products": {
                    "read_permission": True,
                },
            },
        }

        for role_code, element_rules in rules.items():
            for element_code, permissions in element_rules.items():
                AccessRule.objects.update_or_create(
                    role=roles[role_code],
                    element=elements[element_code],
                    defaults=self._rule_defaults(permissions),
                )

    def _rule_defaults(self, permissions: dict[str, bool]) -> dict[str, bool]:
        defaults = {
            "read_permission": False,
            "read_all_permission": False,
            "create_permission": False,
            "update_permission": False,
            "update_all_permission": False,
            "delete_permission": False,
            "delete_all_permission": False,
        }
        defaults.update(permissions)
        return defaults