from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import EmailVerificationToken

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        verification_token = get_object_or_404(EmailVerificationToken, token=token)

        if not verification_token.is_valid():
            return Response(
                {'error': 'Токен истек'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = verification_token.user
        user.is_verified = True
        user.save()

        # Delete token after verification
        verification_token.delete()

        return Response(
            {'message': 'Email успешно подтвержден'},
            status=status.HTTP_200_OK
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
