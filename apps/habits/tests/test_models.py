import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.habits.models import Habit

User = get_user_model()


@pytest.mark.django_db
class TestHabitModel:
    def test_create_habit_success(self, user_factory, place_factory):
        user = user_factory()
        place = place_factory(owner=user)

        habit = Habit.objects.create(
            owner=user,
            name="Test Habit",
            place=place,
            action="Test habit",
            time="10:00:00",
            time_to_complete=60,
            frequency=1,
        )

        assert habit.id is not None
        assert habit.action == "Test habit"

    def test_habit_validation_time_to_complete(self, user_factory):
        user = user_factory()
        habit = Habit(
            owner=user,
            name="Test Habit",
            action="Test habit",
            time="10:00:00",
            time_to_complete=121,  # > 120
            frequency=1,
        )

        with pytest.raises(ValidationError) as exc:
            habit.full_clean()
        assert "time_to_complete" in str(exc.value)

    def test_habit_validation_frequency(self, user_factory):
        user = user_factory()
        habit = Habit(
            owner=user,
            name="Test Habit",
            action="Test habit",
            time="10:00:00",
            time_to_complete=60,
            frequency=8,  # > 7
        )

        with pytest.raises(ValidationError) as exc:
            habit.full_clean()
        assert "frequency" in str(exc.value)
