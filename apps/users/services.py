from django.db import transaction
from django.utils import timezone
from apps.users.jwt import create_access_token
from apps.users.models import AuthSession, User
from apps.users.passwords import check_password, hash_password
from rest_framework.exceptions import AuthenticationFailed

@transaction.atomic
def register_user(validated_data: dict) -> User:
    password = validated_data.pop("password")
    validated_data.pop("password_repeat", None)

    user = User.objects.create(
        **validated_data,
        password_hash=hash_password(password),
    )
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