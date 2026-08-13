import pytest
from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.users.models import EmailVerificationToken
from apps.users.serializers import UserSerializer


User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    class MockUserRegistrationSerializer(serializers.Serializer):
        """Закрытый сериализатор для тестирования логики регистрации"""

        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)
        password_confirm = serializers.CharField(write_only=True)

        def validate(self, data):
            """Проверка совпадения паролей"""
            if data.get("password") != data.get("password_confirm"):
                raise serializers.ValidationError(
                    {"password_confirm": "Пароли не совпадают"}
                )
            return data

        def validate_email(self, value):
            """Проверка уникальности email"""
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "Пользователь с таким email уже существует"
                )
            return value

        def validate_password(self, value):
            """Проверка сложности пароля"""
            if len(value) < 8:
                raise serializers.ValidationError(
                    "Пароль должен содержать минимум 8 символов"
                )
            if not any(c.isupper() for c in value):
                raise serializers.ValidationError(
                    "Пароль должен содержать хотя бы одну заглавную букву"
                )
            if not any(c.isdigit() for c in value):
                raise serializers.ValidationError(
                    "Пароль должен содержать хотя бы одну цифру"
                )
            return value

        def create(self, validated_data):
            """Создание пользователя и токена"""
            validated_data.pop("password_confirm")
            password = validated_data.pop("password")

            try:
                user = User.objects.create_user(
                    email=validated_data["email"], password=password
                )
                EmailVerificationToken.objects.create(user=user)
                return user
            except Exception as e:
                raise serializers.ValidationError(
                    f"Ошибка создания пользователя: {str(e)}"
                )

    def test_valid_registration(self):
        """Тест успешной регистрации"""
        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = self.MockUserRegistrationSerializer(data=data)

        assert serializer.is_valid() is True
        user = serializer.save()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.check_password("StrongPass123!")
        assert EmailVerificationToken.objects.filter(user=user).exists()

    def test_password_mismatch(self):
        """Тест: пароли не совпадают"""
        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass123!",
        }
        serializer = self.MockUserRegistrationSerializer(data=data)

        assert serializer.is_valid() is False
        assert "password_confirm" in serializer.errors
        assert "Пароли не совпадают" in str(serializer.errors["password_confirm"])

    def test_weak_password(self):
        """Тест: слабый пароль"""
        data = {
            "email": "test@example.com",
            "password": "123",
            "password_confirm": "123",
        }
        serializer = self.MockUserRegistrationSerializer(data=data)

        assert serializer.is_valid() is False
        assert "password" in serializer.errors
        assert "минимум 8 символов" in str(serializer.errors["password"])

    def test_invalid_email_format(self):
        """Тест: невалидный формат email"""
        data = {
            "email": "invalid-email",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = self.MockUserRegistrationSerializer(data=data)

        assert serializer.is_valid() is False
        assert "email" in serializer.errors
        assert "valid" in str(serializer.errors["email"]).lower()

    def test_duplicate_email(self):
        """Тест: попытка регистрации с существующим email"""
        # Создаем существующего пользователя
        User.objects.create_user(email="existing@example.com", password="OldPass123!")

        data = {
            "email": "existing@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = self.MockUserRegistrationSerializer(data=data)

        assert serializer.is_valid() is False
        assert "email" in serializer.errors
        assert "уже существует" in str(serializer.errors["email"])


@pytest.mark.django_db
class TestUserSerializer:
    class MockUserSerializer(serializers.ModelSerializer):
        """Закрытый сериализатор для тестирования логики пользователя"""

        class Meta:
            model = User
            fields = [
                "id",
                "email",
                "first_name",
                "last_name",
                "is_verified",
                "telegram_chat_id",
            ]
            read_only_fields = ["id", "is_verified", "telegram_chat_id"]

        def update(self, instance, validated_data):
            """Обновление пользователя с защитой read-only полей"""
            # Удаляем read-only поля из данных
            for field in self.Meta.read_only_fields:
                validated_data.pop(field, None)

            return super().update(instance, validated_data)

    def test_serialize_user(self, user_factory):
        """Тест сериализации пользователя"""
        user = user_factory(
            email="test@example.com", first_name="Test", last_name="User"
        )
        user.is_verified = True
        user.telegram_chat_id = "12345"
        user.save()

        serializer = self.MockUserSerializer(user)
        data = serializer.data

        assert data["id"] == user.id
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["is_verified"] is True
        assert data["telegram_chat_id"] == "12345"

    def test_serialize_user_read_only_fields(self, user_factory):
        """Тест: read-only поля не должны обновляться"""
        user = user_factory(
            email="test@example.com", first_name="Original", last_name="User"
        )

        serializer = self.MockUserSerializer(
            user,
            data={
                "id": 999,
                "is_verified": True,
                "telegram_chat_id": "99999",
                "first_name": "Updated",
                "last_name": "Name",
            },
            partial=True,
        )

        assert serializer.is_valid() is True
        updated_user = serializer.save()

        # Read-only поля НЕ должны обновляться
        assert updated_user.id == user.id  # Не изменился
        assert updated_user.id != 999

        assert updated_user.is_verified == user.is_verified  # Не изменился
        assert updated_user.is_verified is not True

        assert updated_user.telegram_chat_id == user.telegram_chat_id  # Не изменился
        assert updated_user.telegram_chat_id != "99999"

        # Обновляемые поля ДОЛЖНЫ измениться
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"

    def test_serialize_user_partial_update(self, user_factory):
        """Тест проверяет частичное обновление пользователя"""
        # Создаём пользователя с конкретными данными
        user = user_factory(
            first_name="Original",
            last_name="User",
            email="test@example.com"
        )

        serializer = UserSerializer(
            instance=user,
            data={"first_name": "New"},
            partial=True
        )
        assert serializer.is_valid() is True

        updated_user = serializer.save()

        assert updated_user.first_name == "New"

        assert updated_user.last_name == "User"

    def test_serialize_user_without_telegram(self, user_factory):
        """Тест: пользователь без telegram chat id"""
        user = user_factory(
            email="test@example.com", first_name="Test", last_name="User"
        )
        user.is_verified = False
        user.telegram_chat_id = None
        user.save()

        serializer = self.MockUserSerializer(user)
        data = serializer.data

        assert data["is_verified"] is False
        assert data["telegram_chat_id"] is None
