from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from django.db import IntegrityError
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.viewsets import GenericViewSet
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import UserLoginSerializer, UserRegisterSerializer


class AuthViewSet(GenericViewSet):

    def get_serializer_class(self):
        if self.action == "login":
            return UserLoginSerializer
        elif self.action == "register":
            return UserRegisterSerializer

    @swagger_auto_schema(
        operation_summary="Login",
        operation_description="Login user with email and password. Returns access and refresh tokens.",
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(email=email, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Register",
        operation_description="Register user with email and password. Returns access and refresh tokens.",
    )
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email", None)
        password = serializer.validated_data.get("password", None)
        full_name = serializer.validated_data.get("full_name", None)

        try:
            user = CustomUser.objects.create_user(
                password=password,
                email=email,
                full_name=full_name,
            )
        except IntegrityError:
            return Response({"error": f"User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"error": "".join(e)}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response(
            {
                "access_token": access_token,
                "refresh_token": str(refresh),
            },
            status=status.HTTP_201_CREATED
        )
