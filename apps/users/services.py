from django.db import transaction
from django.utils import timezone
from apps.users.jwt import create_access_token
from apps.users.models import AuthSession, User
from apps.users.passwords import check_password, hash_password
from rest_framework.exceptions import AuthenticationFailed
from apps.access.models import Role, UserRole

@transaction.atomic
def register_user(validated_data: dict) -> User:
    password = validated_data.pop("password")
    validated_data.pop("password_repeat", None)
    user = User.objects.create(
        **validated_data,
        password_hash=hash_password(password),
    )
    default_role, _ = Role.objects.get_or_create(
        code="user",
        defaults={"name": "User", "description": "Default registered user"},
    )
    UserRole.objects.create(user=user, role=default_role)
    
    return user



def login_user(email: str, password: str) -> str:
    try:
        user = User.objects.get(email=email.lower(), is_active=True)
    except User.DoesNotExist as error:
        raise AuthenticationFailed("Invalid email or password") from error

    if not check_password(password, user.password_hash):
        raise AuthenticationFailed("Invalid email or password")

    return create_access_token(user)


def logout_by_payload(payload: dict) -> None:
    AuthSession.objects.filter(token_jti=payload["jti"], revoked_at__isnull=True).update(
        revoked_at=timezone.now()
    )