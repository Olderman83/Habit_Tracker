from django.urls import path
from .views import (
    PlaceListCreateView,
    HabitListCreateView,
    HabitPublicListView
)

urlpatterns = [
    # Places
    path('places/', PlaceListCreateView.as_view(), name='place-list-create'),
    path('', HabitListCreateView.as_view(), name='habit-list-create'),
    path('public/', HabitPublicListView.as_view(), name='habit-public-list'),
]
