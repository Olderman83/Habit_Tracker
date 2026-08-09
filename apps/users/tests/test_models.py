import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.users.models import EmailVerificationToken

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_success(self, user_factory):
        user = user_factory(email="test@example.com", password="testpass123")
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_verified is False
        assert user.username is None

    def test_create_user_without_email_raises_error(self):
        with pytest.raises(ValueError) as exc:
            User.objects.create_user(email=None, password="testpass123")
        assert "Email обязателен" in str(exc.value)

    def test_create_superuser_success(self, user_factory):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123"
        )

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True

    def test_create_superuser_without_staff_raises_error(self):
        with pytest.raises(ValueError) as exc:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_staff=False
            )
        assert "is_staff=True" in str(exc.value)

    def test_user_str_method(self, user_factory):
        user = user_factory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_user_email_index(self, user_factory):
        user = user_factory(email="test@example.com")
        # Check that user is saved and has an id
        assert user.id is not None


@pytest.mark.django_db
class TestEmailVerificationTokenModel:
    def test_create_token_success(self, user_factory):
        user = user_factory()
        token = EmailVerificationToken.objects.create(user=user)

        assert token.id is not None
        assert token.token is not None
        assert len(token.token) == 43  # secrets.token_urlsafe(32) returns 43 chars
        assert token.expires_at > timezone.now()
        assert token.is_valid() is True

    def test_token_expires(self, user_factory):
        user = user_factory()
        token = EmailVerificationToken.objects.create(user=user)

        # Manually set expiration to past
        token.expires_at = timezone.now() - timezone.timedelta(hours=1)
        token.save()

        assert token.is_valid() is False

    def test_token_unique_constraint(self, user_factory):
        user1 = user_factory(email="user1@example.com")
        user2 = user_factory(email="user2@example.com")

        token1 = EmailVerificationToken.objects.create(user=user1)

        # Try to create another token with same user (OneToOneField)
        with pytest.raises(Exception):  # IntegrityError
            EmailVerificationToken.objects.create(user=user1)

        # Try to create token for user2
        token2 = EmailVerificationToken.objects.create(user=user2)
        assert token2.id is not None
        assert token2.token != token1.token

    def test_token_str_method(self, user_factory):
        user = user_factory()
        token = EmailVerificationToken.objects.create(user=user)
        assert str(token) == f"Token for {user.email}"

    def test_token_auto_generation(self, user_factory):
        user = user_factory()
        token = EmailVerificationToken.objects.create(user=user)

        # Token should be automatically generated
        assert token.token is not None
        assert len(token.token) > 0

    def test_token_expires_auto_set(self, user_factory):
        user = user_factory()
        token = EmailVerificationToken.objects.create(user=user)

        assert token.expires_at is not None
        # Should be approximately 24 hours from now
        diff = token.expires_at - timezone.now()
        assert 23 <= diff.total_seconds() / 3600 <= 25
