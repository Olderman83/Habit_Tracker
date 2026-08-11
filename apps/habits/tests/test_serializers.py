import pytest
from apps.habits.serializers import HabitSerializer, PlaceSerializer


@pytest.mark.django_db
class TestPlaceSerializer:
    def test_valid_place_serializer(self, user_factory):
        user = user_factory()
        data = {'name': 'Home Office'}

        serializer = PlaceSerializer(data=data, context={'request': None})
        assert serializer.is_valid() is True

        place = serializer.save(owner=user)
        assert place.name == 'Home Office'
        assert place.owner == user

    def test_place_name_too_short(self):
        data = {'name': 'A'}
        serializer = PlaceSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'name' in serializer.errors
        assert 'минимум 2 символа' in str(serializer.errors['name'])

    def test_place_serializer_read_only_fields(self, place_factory, user_factory):
        user = user_factory()
        place = place_factory(owner=user, name='Test Place')

        serializer = PlaceSerializer(place)
        data = serializer.data

        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert data['name'] == 'Test Place'


@pytest.mark.django_db
class TestHabitSerializer:
    def test_valid_habit_serializer(self, user_factory, place_factory):
        user = user_factory()
        place = place_factory(owner=user)

        data = {
            'place': place.id,
            'action': 'Morning Run',
            'time': '07:00:00',
            'frequency': 1,
            'time_to_complete': 60,
            'is_public': False,
            'is_pleasant': False
        }

        serializer = HabitSerializer(data=data, context={'request': type('Request', (), {'user': user})()})
        assert serializer.is_valid() is True

        habit = serializer.save(owner=user)
        assert habit.action == 'Morning Run'
        assert habit.owner == user

    def test_habit_with_reward_and_linked_habit(self, user_factory, habit_factory, place_factory):
        user = user_factory()
        place = place_factory(owner=user)
        pleasant_habit = habit_factory(owner=user, place=place, is_pleasant=True)

        data = {
            'place': place.id,
            'action': 'Workout',
            'time': '08:00:00',
            'frequency': 1,
            'time_to_complete': 60,
            'reward': 'Watch movie',
            'linked_habit': pleasant_habit.id
        }

        serializer = HabitSerializer(data=data, context={'request': user})
        assert serializer.is_valid() is False
        assert 'linked_habit' in serializer.errors

    def test_habit_time_to_complete_exceeds_limit(self, user_factory):
        user = user_factory()

        data = {
            'action': 'Workout',
            'time': '08:00:00',
            'frequency': 1,
            'time_to_complete': 121
        }

        serializer = HabitSerializer(data=data, context={'request': user})
        assert serializer.is_valid() is False
        assert 'time_to_complete' in serializer.errors

    def test_pleasant_habit_with_reward(self, user_factory):
        user = user_factory()

        data = {
            'action': 'Read book',
            'time': '20:00:00',
            'frequency': 1,
            'time_to_complete': 60,
            'is_pleasant': True,
            'reward': 'Chocolate'
        }

        serializer = HabitSerializer(data=data, context={'request': user})
        assert serializer.is_valid() is False
        assert 'reward' in serializer.errors

    def test_habit_with_linked_non_pleasant_habit(self, user_factory, habit_factory, place_factory):
        user = user_factory()
        place = place_factory(owner=user)
        non_pleasant_habit = habit_factory(owner=user, place=place, is_pleasant=False)

        data = {
            'place': place.id,
            'action': 'Workout',
            'time': '08:00:00',
            'frequency': 1,
            'time_to_complete': 60,
            'linked_habit': non_pleasant_habit.id
        }

        serializer = HabitSerializer(data=data, context={'request': user})
        assert serializer.is_valid() is False
        assert 'linked_habit' in serializer.errors

    def test_habit_frequency_out_of_range(self, user_factory):
        user = user_factory()

        data = {
            'action': 'Workout',
            'time': '08:00:00',
            'frequency': 8,
            'time_to_complete': 60
        }

        serializer = HabitSerializer(data=data, context={'request': user})
        assert serializer.is_valid() is False
        assert 'frequency' in serializer.errors

    def test_habit_serializer_read_only_fields(self, habit_factory, user_factory, place_factory):
        user = user_factory()
        place = place_factory(owner=user)
        habit = habit_factory(owner=user, place=place, action='Test Habit')

        serializer = HabitSerializer(habit)
        data = serializer.data

        assert 'id' in data
        assert 'owner' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert data['action'] == 'Test Habit'
