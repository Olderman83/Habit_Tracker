from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Habit, Place
from .serializers import HabitSerializer, HabitPublicSerializer, PlaceSerializer
from .permissions import IsOwner
from .pagination import HabitPagination


class PlaceListCreateView(generics.ListCreateAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination

    def get_queryset(self):
        return Place.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PlaceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Place.objects.filter(owner=self.request.user)


class HabitListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_pleasant', 'is_public', 'is_active']
    ordering_fields = ['time', 'created_at']
    ordering = ['time']

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)


class HabitPublicListView(generics.ListAPIView):
    serializer_class = HabitPublicSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'time']
    ordering_fields = ['time', 'created_at']
    ordering = ['time']

    def get_queryset(self):
        return Habit.objects.filter(is_public=True, is_active=True)
