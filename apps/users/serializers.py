from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from .models import User, EmailVerificationToken
import json
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "password_confirm")

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают"}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)

        # Create verification token
        token = EmailVerificationToken.objects.create(user=user)

        # Send verification email (stub)
        self.send_verification_email(user, token)

        return user

    def send_verification_email(self, user, token):
        email_content = {
            "to": user.email,
            "subject": "Подтверждение email",
            "body": f"Перейдите по ссылке для подтверждения: http://localhost:8000/api/users/verify/{token.token}/",
            "token": token.token,
            "user_id": user.id,
        }

        # Save to file
        emails_dir = Path(settings.EMAIL_FILE_PATH)
        emails_dir.mkdir(parents=True, exist_ok=True)
        file_path = emails_dir / f"{user.id}_{token.token[:8]}.json"
        with open(file_path, "w") as f:
            json.dump(email_content, f, indent=2)

        # Also try to send real email if configured
        try:
            send_mail(
                email_content["subject"],
                email_content["body"],
                None,
                [email_content["to"]],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Unexpected error sending email to {user.email}: {e}")
            return False


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_verified",
            "telegram_chat_id",
        )
        read_only_fields = ("id", "is_verified")
