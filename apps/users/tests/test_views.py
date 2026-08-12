import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.users.models import EmailVerificationToken
from django.utils import timezone


User = get_user_model()


@pytest.fixture
def api_client():
    """Фикстура для API клиента"""
    return APIClient()


@pytest.mark.django_db
class TestUserRegistrationView:
    def test_registration_success(self, api_client):
        url = reverse("register")
        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="test@example.com").exists()

        user = User.objects.get(email="test@example.com")
        assert user.is_verified is False

        # Check that verification token was created
        assert EmailVerificationToken.objects.filter(user=user).exists()

    def test_registration_password_mismatch(self, api_client):
        url = reverse("register")
        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass123!",
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(email="test@example.com").exists()

    def test_registration_duplicate_email(self, api_client, user_factory):
        user_factory(email="test@example.com")

        url = reverse("register")
        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data


@pytest.mark.django_db
class TestEmailVerificationView:
    def test_verification_success(self, api_client, user_factory):
        user = user_factory(is_verified=False)
        token = EmailVerificationToken.objects.create(user=user)

        url = reverse("verify-email", kwargs={"token": token.token})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Email успешно подтвержден"

        user.refresh_from_db()
        assert user.is_verified is True

        # Token should be deleted
        assert not EmailVerificationToken.objects.filter(user=user).exists()

    def test_verification_invalid_token(self, api_client):
        url = reverse("verify-email", kwargs={"token": "invalid-token"})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_verification_expired_token(self, api_client, user_factory):
        user = user_factory(is_verified=False)
        token = EmailVerificationToken.objects.create(user=user)
        token.expires_at = timezone.now() - timezone.timedelta(hours=1)
        token.save()

        url = reverse("verify-email", kwargs={"token": token.token})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Токен истек"

        user.refresh_from_db()
        assert user.is_verified is False


@pytest.mark.django_db
class TestUserProfileView:
    def test_get_profile_authenticated(self, api_client, user_factory):
        user = user_factory(
            email="test@example.com", first_name="Test", last_name="User"
        )
        api_client.force_authenticate(user=user)

        url = reverse("profile")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "test@example.com"
        assert response.data["first_name"] == "Test"
        assert response.data["last_name"] == "User"

    def test_get_profile_unauthenticated(self, api_client):
        url = reverse("profile")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, api_client, user_factory):
        user = user_factory(email="test@example.com")
        api_client.force_authenticate(user=user)

        url = reverse("profile")
        data = {"first_name": "Updated", "last_name": "Name"}
        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "Name"

    def test_update_profile_read_only_fields(self, api_client, user_factory):
        user = user_factory(email="test@example.com", is_verified=False)
        api_client.force_authenticate(user=user)

        url = reverse("profile")
        data = {"is_verified": True, "telegram_chat_id": "12345"}
        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()

        # These fields should be read-only
        assert user.is_verified is False
        assert user.telegram_chat_id is None
