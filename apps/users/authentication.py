import jwt
from rest_framework import authentication, exceptions

from apps.users.jwt import decode_access_token
from apps.users.models import AuthSession, User


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate_header(self, request) -> str:
        return self.keyword

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        try:
            keyword, token = header.split(" ", 1)
        except ValueError as error:
            raise exceptions.AuthenticationFailed("Invalid Authorization header") from error

        if keyword != self.keyword:
            return None

        try:
            payload = decode_access_token(token)
        except jwt.ExpiredSignatureError as error:
            raise exceptions.AuthenticationFailed("Token expired") from error
        except jwt.InvalidTokenError as error:
            raise exceptions.AuthenticationFailed("Invalid token") from error

        user = self._get_active_user(payload)
        self._validate_session(payload)
        return user, payload

    def _get_active_user(self, payload: dict) -> User:
        try:
            return User.objects.get(id=payload["sub"], is_active=True)
        except User.DoesNotExist as error:
            raise exceptions.AuthenticationFailed("User is inactive or not found") from error

    def _validate_session(self, payload: dict) -> None:
        try:
            session = AuthSession.objects.get(token_jti=payload["jti"])
        except AuthSession.DoesNotExist as error:
            raise exceptions.AuthenticationFailed("Session not found") from error

        if not session.is_active:
            raise exceptions.AuthenticationFailed("Session revoked")
