from django.db import models


class Role(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "roles"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code
    

class BusinessElement(models.Model):
    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "business_elements"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code
    

class AccessRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="rules")
    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name="rules",
    )
    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        db_table = "access_rules"
        constraints = [
            models.UniqueConstraint(
                fields=["role", "element"],
                name="unique_access_rule_for_role_and_element",
            )
        ]



class UserRole(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="role_links",
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_links")

    class Meta:
        db_table = "user_roles"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                name="unique_user_role",
            )
        ]