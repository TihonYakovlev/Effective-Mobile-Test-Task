import uuid
from datetime import datetime, timezone

import jwt
from django.conf import settings
from django.utils import timezone as django_timezone

from apps.users.models import AuthSession, User


def create_access_token(user: User) -> str:
    now = django_timezone.now()
    expires_at = now + settings.JWT_ACCESS_TOKEN_TTL
    token_jti = uuid.uuid4()

    AuthSession.objects.create(
        user=user,
        token_jti=token_jti,
        expires_at=expires_at,
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "jti": str(token_jti),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )