import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.habits.models import Place, Habit

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an instance of APIClient"""
    return APIClient()


@pytest.fixture
def user_factory(db):
    def create_user(email="test@example.com", password="testpass123", **kwargs):
        return User.objects.create_user(email=email, password=password, **kwargs)
    return create_user


@pytest.fixture
def place_factory(db):
    def create_place(owner, name="Test Place"):
        return Place.objects.create(owner=owner, name=name)
    return create_place


@pytest.fixture
def habit_factory(db):
    def create_habit(owner, place=None, action="Test habit", time="10:00:00",
                     time_to_complete=60, frequency=1, **kwargs):
        return Habit.objects.create(
            owner=owner,
            place=place,
            action=action,
            time=time,
            time_to_complete=time_to_complete,
            frequency=frequency,
            **kwargs
        )
    return create_habit


@pytest.fixture
def authenticated_client(db, user_factory):
    """Return an authenticated API client"""
    user = user_factory()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user
