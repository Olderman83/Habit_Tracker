from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Create superuser automatically if not exists'

    def handle(self, *args, **options):
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123456')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} created successfully'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {email} already exists'))