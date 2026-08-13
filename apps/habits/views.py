from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)
from .models import Habit, Place
from .serializers import HabitSerializer, HabitPublicSerializer, PlaceSerializer
from .pagination import HabitPagination
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .serializers import PlaceSerializer
from .permissions import IsOwnerOrReadOnly


class PlaceListCreateView(generics.ListCreateAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination

    @extend_schema(
        summary="Создание нового места",
        description="Создает новое место для текущего пользователя",
        request=PlaceSerializer,
        responses={
            201: PlaceSerializer,
            400: OpenApiResponse(description="Ошибка валидации данных"),
            401: OpenApiResponse(description="Неавторизованный доступ"),
        },
        examples=[
            OpenApiExample("Пример запроса", value={"name": "Дом"}, request_only=True)
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Place.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["is_pleasant", "is_public", "is_active"]
    ordering_fields = ["time", "created_at"]
    ordering = ["time"]

    @extend_schema(
        summary="Получение списка привычек",
        description="""
            Возвращает список привычек текущего пользователя.

            Доступна фильтрация и сортировка:
            - `is_pleasant` - фильтр по типу привычки
            - `is_public` - фильтр по публичности
            - `is_active` - фильтр по активности
            - `ordering` - сортировка по time, created_at
            """,
        parameters=[
            OpenApiParameter(
                name="is_pleasant",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Фильтр по типу привычки (true - приятная, false - полезная)",
                required=False,
            ),
            OpenApiParameter(
                name="is_public",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Фильтр по публичности",
                required=False,
            ),
            OpenApiParameter(
                name="is_active",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Фильтр по активности",
                required=False,
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Сортировка (time, -time, created_at, -created_at)",
                required=False,
                examples=[
                    OpenApiExample("По времени", value="time"),
                    OpenApiExample("По времени убывание", value="-time"),
                ],
            ),
        ],
        responses={
            200: HabitSerializer(many=True),
            401: OpenApiResponse(description="Неавторизованный доступ"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Создание новой привычки",
        description="""
            Создает новую привычку для текущего пользователя.

            Правила валидации:
            1. Приятная привычка не может иметь вознаграждение или связанную привычку
            2. У полезной привычки может быть либо вознаграждение, либо связанная привычка (не вместе)
            3. Связанная привычка должна быть приятной
            4. Время выполнения не должно превышать 120 секунд
            5. Периодичность от 1 до 7 дней
            """,
        request=HabitSerializer,
        responses={
            201: HabitSerializer,
            400: OpenApiResponse(
                description="Ошибка валидации данных",
                response={
                    "type": "object",
                    "properties": {
                        "linked_habit": {"type": "array", "items": {"type": "string"}},
                        "reward": {"type": "array", "items": {"type": "string"}},
                        "time_to_complete": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            ),
            401: OpenApiResponse(description="Неавторизованный доступ"),
        },
        examples=[
            OpenApiExample(
                "Полезная привычка с вознаграждением",
                value={
                    "action": "Делать зарядку",
                    "time": "08:00:00",
                    "frequency": 1,
                    "time_to_complete": 60,
                    "reward": "Кофе с пирожным",
                    "is_pleasant": False,
                    "is_public": False,
                    "place": 1,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Полезная привычка со связанной привычкой",
                value={
                    "action": "Изучать Python",
                    "time": "20:00:00",
                    "frequency": 2,
                    "time_to_complete": 30,
                    "linked_habit": 2,
                    "is_pleasant": False,
                    "is_public": True,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Приятная привычка",
                value={
                    "action": "Смотреть любимый сериал",
                    "time": "22:00:00",
                    "frequency": 1,
                    "time_to_complete": 120,
                    "is_pleasant": True,
                    "is_public": False,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitPublicListView(generics.ListAPIView):
    serializer_class = HabitPublicSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["action", "time"]
    ordering_fields = ["time", "created_at"]
    ordering = ["time"]

    @extend_schema(
        summary="Получение публичных привычек",
        description="""
            Возвращает список публичных привычек всех пользователей.

            Доступна фильтрация и сортировка:
            - `action` - фильтр по действию
            - `time` - фильтр по времени
            - `ordering` - сортировка по time, created_at
            """,
        parameters=[
            OpenApiParameter(
                name="action",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по действию",
                required=False,
            ),
            OpenApiParameter(
                name="time",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по времени",
                required=False,
            ),
        ],
        responses={
            200: HabitPublicSerializer(many=True),
            401: OpenApiResponse(description="Неавторизованный доступ"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Habit.objects.filter(is_public=True, is_active=True)

class PlaceRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsOwnerOrReadOnly]
