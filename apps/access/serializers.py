from rest_framework import serializers

from apps.access.models import AccessRule, BusinessElement, Role, UserRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "name", "description"]


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = ["id", "code", "name", "description"]


class AccessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRule
        fields = [
            "id",
            "role",
            "element",
            "read_permission",
            "read_all_permission",
            "create_permission",
            "update_permission",
            "update_all_permission",
            "delete_permission",
            "delete_all_permission",
        ]