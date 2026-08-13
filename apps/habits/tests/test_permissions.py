import pytest
from apps.habits.permissions import IsOwner, IsOwnerOrReadOnly, IsPublicReadOnly
from django.contrib.auth import get_user_model
from unittest.mock import Mock

User = get_user_model()


@pytest.mark.django_db
class TestIsOwnerPermission:
    def test_owner_has_permission(self, user_factory, habit_factory):
        user = user_factory()
        habit = habit_factory(owner=user, name="Test Habit")

        permission = IsOwner()
        request = Mock()
        request.user = user

        assert permission.has_object_permission(request, None, habit) is True

    def test_non_owner_has_no_permission(self, user_factory, habit_factory):
        user1 = user_factory(email="user1@example.com")
        user2 = user_factory(email="user2@example.com")
        habit = habit_factory(owner=user1, name="Test Habit")

        permission = IsOwner()
        request = Mock()
        request.user = user2

        assert permission.has_object_permission(request, None, habit) is False


@pytest.mark.django_db
class TestIsOwnerOrReadOnlyPermission:
    def test_owner_has_permission_for_modification(self, user_factory, habit_factory):
        user = user_factory()
        habit = habit_factory(owner=user, name="Test Habit")

        permission = IsOwnerOrReadOnly()
        request = Mock()
        request.user = user
        request.method = "PUT"

        assert permission.has_object_permission(request, None, habit) is True

    def test_non_owner_has_read_permission(self, user_factory, habit_factory):
        user1 = user_factory(email="user1@example.com")
        user2 = user_factory(email="user2@example.com")
        habit = habit_factory(owner=user1, name="Test Habit")

        permission = IsOwnerOrReadOnly()
        request = Mock()
        request.user = user2
        request.method = "GET"

        assert permission.has_object_permission(request, None, habit) is True

    def test_non_owner_has_no_modification_permission(
        self, user_factory, habit_factory
    ):
        user1 = user_factory(email="user1@example.com")
        user2 = user_factory(email="user2@example.com")
        habit = habit_factory(owner=user1, name="Test Habit")

        permission = IsOwnerOrReadOnly()
        request = Mock()
        request.user = user2
        request.method = "PUT"

        assert permission.has_object_permission(request, None, habit) is False


@pytest.mark.django_db
class TestIsPublicReadOnlyPermission:
    def test_anyone_can_read_public_habit(self, user_factory, habit_factory):
        user1 = user_factory(email="user1@example.com")
        user2 = user_factory(email="user2@example.com")
        habit = habit_factory(owner=user1, is_public=True, name="Test Habit")

        permission = IsPublicReadOnly()
        request = Mock()
        request.user = user2
        request.method = "GET"

        assert permission.has_object_permission(request, None, habit) is True

    def test_only_owner_can_modify_public_habit(self, user_factory, habit_factory):
        user1 = user_factory(email="user1@example.com")
        user2 = user_factory(email="user2@example.com")
        habit = habit_factory(owner=user1, is_public=True, name="Test Habit")

        permission = IsPublicReadOnly()

        # Owner can modify
        request = Mock()
        request.user = user1
        request.method = "PUT"
        assert permission.has_object_permission(request, None, habit) is True

        # Non-owner cannot modify
        request = Mock()
        request.user = user2
        request.method = "PUT"
        assert permission.has_object_permission(request, None, habit) is False

    def test_only_owner_can_access_private_habit(self, user_factory, habit_factory):
        user1 = user_factory(email="user1@example.com")
        user2 = user_factory(email="user2@example.com")
        habit = habit_factory(owner=user1, is_public=False, name="Test Habit")

        permission = IsPublicReadOnly()

        # Owner can access
        request = Mock()
        request.user = user1
        request.method = "GET"
        assert permission.has_object_permission(request, None, habit) is True

        # Non-owner cannot access private habit
        request = Mock()
        request.user = user2
        request.method = "GET"
        assert permission.has_object_permission(request, None, habit) is False
