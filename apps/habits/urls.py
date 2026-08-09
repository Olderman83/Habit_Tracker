from django.urls import path
from .views import (
    PlaceListCreateView, PlaceRetrieveUpdateDestroyView,
    HabitListCreateView, HabitRetrieveUpdateDestroyView,
    HabitPublicListView
)

urlpatterns = [
    # Places
    path('places/', PlaceListCreateView.as_view(), name='place-list-create'),
    path('places/<int:pk>/', PlaceRetrieveUpdateDestroyView.as_view(), name='place-detail'),

    # Habits
    path('', HabitListCreateView.as_view(), name='habit-list-create'),
    path('<int:pk>/', HabitRetrieveUpdateDestroyView.as_view(), name='habit-detail'),
    path('public/', HabitPublicListView.as_view(), name='habit-public-list'),
]
