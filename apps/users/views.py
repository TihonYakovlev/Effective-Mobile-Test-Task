from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer
from apps.users.services import login_user, logout_by_payload, register_user


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "middle_name": request.user.middle_name,
            }
        )


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
        token = login_user(**serializer.validated_data)
        return Response({"access_token": token, "token_type": "Bearer"})


class LogoutView(APIView):
    def post(self, request):
        logout_by_payload(request.auth)
        return Response(status=status.HTTP_204_NO_CONTENT)