import pytest
from django.urls import reverse
from rest_framework import status
from apps.habits.models import Habit, Place


@pytest.mark.django_db
class TestPlaceViews:
    def test_create_place(self, api_client, user_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        url = reverse('place-list-create')
        data = {'name': 'Gym'}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Place.objects.filter(name='Gym', owner=user).exists()

    def test_list_places(self, api_client, user_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        place1 = place_factory(owner=user, name='Home')
        place2 = place_factory(owner=user, name='Office')

        url = reverse('place-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['results'][0]['name'] == 'Home'

        place_names = [place['name'] for place in response.data['results']]
        assert place1.name in place_names
        assert place2.name in place_names

        place_ids = [place['id'] for place in response.data['results']]
        assert place1.id in place_ids
        assert place2.id in place_ids

    def test_update_place(self, api_client, user_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        place = place_factory(owner=user, name='Old Name')
        url = reverse('place-detail', kwargs={'pk': place.id})
        data = {'name': 'New Name'}

        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK

        place.refresh_from_db()
        assert place.name == 'New Name'

    def test_delete_place(self, api_client, user_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        place = place_factory(owner=user)
        url = reverse('place-detail', kwargs={'pk': place.id})

        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Place.objects.filter(id=place.id).exists()


@pytest.mark.django_db
class TestHabitViews:
    def test_create_habit(self, api_client, user_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)
        place = place_factory(owner=user)

        url = reverse('habit-list-create')
        data = {
            'place': place.id,
            'action': 'Morning Run',
            'time': '07:00:00',
            'frequency': 1,
            'time_to_complete': 60
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Habit.objects.filter(action='Morning Run', owner=user).exists()

    def test_list_habits(self, api_client, user_factory, habit_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        place = place_factory(owner=user, name='Test Place')

        habit1 = habit_factory(owner=user, action='Habit 1', place=place)
        habit2 = habit_factory(owner=user, action='Habit 2', place=place)

        url = reverse('habit-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

        habit_ids = [habit['id'] for habit in response.data['results']]
        assert habit1.id in habit_ids
        assert habit2.id in habit_ids

        habit_actions = [habit['action'] for habit in response.data['results']]
        assert habit1.action in habit_actions
        assert habit2.action in habit_actions

    def test_list_habits_filter_by_is_pleasant(self, api_client, user_factory, habit_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        place = place_factory(owner=user, name='Test Place')

        habit_factory(owner=user, is_pleasant=True, action='Pleasant 1', place=place)
        habit_factory(owner=user, is_pleasant=False, action='Pleasant 2', place=place)

        url = reverse('habit-list-create') + '?is_pleasant=true'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['is_pleasant'] is True

    def test_update_habit(self, api_client, user_factory, habit_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        place = place_factory(owner=user, name='Test Place')

        habit = habit_factory(owner=user, action='Old Action', place=place)
        url = reverse('habit-detail', kwargs={'pk': habit.id})
        data = {'action': 'New Action'}

        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK

        habit.refresh_from_db()
        assert habit.action == 'New Action'

    def test_delete_habit(self, api_client, user_factory, habit_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        place = place_factory(owner=user, name='Test Place')

        habit = habit_factory(owner=user, place=place)
        url = reverse('habit-detail', kwargs={'pk': habit.id})

        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Habit.objects.filter(id=habit.id).exists()

    def test_list_public_habits(self, api_client, user_factory, habit_factory, place_factory):
        user = user_factory()
        api_client.force_authenticate(user=user)

        place = place_factory(owner=user, name='Test Place')

        habit_factory(owner=user, is_public=True, is_active=True, action='Public 1', place=place)
        habit_factory(owner=user, is_public=False, is_active=True, action='Public 2', place=place)
        habit_factory(owner=user, is_public=True, is_active=False, action='Public 3', place=place)

        url = reverse('habit-public-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['action'] == 'Public 1'

    def test_user_cannot_access_others_habits(self, api_client, user_factory, habit_factory):
        user1 = user_factory(email='user1@example.com')
        user2 = user_factory(email='user2@example.com')

        # Create habit for user2
        habit = habit_factory(owner=user2)

        # Try to access with user1
        api_client.force_authenticate(user=user1)
        url = reverse('habit-detail', kwargs={'pk': habit.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
