from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import EmailVerificationToken
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample,
)


User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        description="Создает нового пользователя и отправляет письмо с ссылкой для подтверждения email",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
                description="Пользователь успешно зарегистрирован",
            ),
            400: OpenApiResponse(description="Ошибка валидации данных"),
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "email": "user@example.com",
                    "password": "SecurePass123",
                    "password_confirm": "SecurePass123",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Подтверждение email",
        description="Подтверждает email пользователя по токену, полученному в письме",
        parameters=[
            OpenApiParameter(
                name="token",
                # ... другие параметры ...
                examples={"example": {"value": "abc123def456..."}},
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Email успешно подтвержден",
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Email успешно подтвержден",
                        }
                    },
                },
            ),
            400: OpenApiResponse(
                description="Токен истек или недействителен",
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Токен истек"}
                    },
                },
            ),
            404: OpenApiResponse(description="Токен не найден"),
        },
        examples=[
            OpenApiExample(
                "Успешное подтверждение",
                value={"message": "Email успешно подтвержден"},
                response_only=True,
            ),
            OpenApiExample(
                "Истекший токен", value={"error": "Токен истек"}, response_only=True
            ),
        ],
    )
    def get(self, request, token):
        verification_token = get_object_or_404(EmailVerificationToken, token=token)

        if not verification_token.is_valid():
            return Response(
                {"error": "Токен истек"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = verification_token.user
        user.is_verified = True
        user.save()

        # Delete token after verification
        verification_token.delete()

        return Response(
            {"message": "Email успешно подтвержден"}, status=status.HTTP_200_OK
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    @extend_schema(
        summary="Получение профиля пользователя",
        description="Возвращает информацию о текущем авторизованном пользователе",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Неавторизованный доступ"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление профиля пользователя",
        description="Обновляет данные текущего авторизованного пользователя",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Ошибка валидации данных"),
            401: OpenApiResponse(description="Неавторизованный доступ"),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление профиля пользователя",
        description="Частично обновляет данные текущего авторизованного пользователя",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Ошибка валидации данных"),
            401: OpenApiResponse(description="Неавторизованный доступ"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user
