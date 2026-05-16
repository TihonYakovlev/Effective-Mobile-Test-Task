from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer
from apps.users.services import login_user, logout_by_payload, register_user


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        request.user.is_active = False
        request.user.deleted_at = timezone.now()
        request.user.save(update_fields=["is_active", "deleted_at", "updated_at"])
        request.user.sessions.filter(revoked_at__isnull=True).update(
            revoked_at=timezone.now()
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(serializer.validated_data)
        return Response(UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = login_user(**serializer.validated_data)
        except AuthenticationFailed as error:
            return Response(
                {"detail": str(error.detail)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response({"access_token": token, "token_type": "Bearer"})


class LogoutView(APIView):
    def post(self, request):
        logout_by_payload(request.auth)
        return Response(status=status.HTTP_204_NO_CONTENT)
