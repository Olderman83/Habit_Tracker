from django.core.exceptions import ValidationError
from apps.habits.models import Habit


def validate_habit(habit):
    """Валидация модели Habit"""
    errors = {}

    # 1. Запрет одновременного выбора связанной привычки и вознаграждения
    if habit.linked_habit and habit.reward:
        errors[
            "linked_habit"
        ] = "Нельзя одновременно указывать связанную привычку и вознаграждение"
        errors[
            "reward"
        ] = "Нельзя одновременно указывать связанную привычку и вознаграждение"

    # 2. Время выполнения не более 120 секунд
    if habit.time_to_complete > 120:
        errors["time_to_complete"] = "Время выполнения не должно превышать 120 секунд"

    # 3. Связанная привычка должна быть приятной
    if habit.linked_habit and not habit.linked_habit.is_pleasant:
        errors["linked_habit"] = "Связанная привычка должна быть приятной"

    # 4. У приятной привычки не может быть вознаграждения или связанной привычки
    if habit.is_pleasant:
        if habit.linked_habit:
            errors[
                "linked_habit"
            ] = "У приятной привычки не может быть связанной привычки"
        if habit.reward:
            errors["reward"] = "У приятной привычки не может быть вознаграждения"

    # 5. Периодичность от 1 до 7 дней
    if habit.frequency < 1 or habit.frequency > 7:
        errors["frequency"] = "Периодичность должна быть от 1 до 7 дней"

    if errors:
        raise ValidationError(errors)


def validate_habit_update(habit, data):
    """Валидация обновления привычки"""
    # Создаем временный экземпляр для валидации
    temp_habit = Habit(
        linked_habit=data.get("linked_habit", habit.linked_habit),
        reward=data.get("reward", habit.reward),
        time_to_complete=data.get("time_to_complete", habit.time_to_complete),
        is_pleasant=data.get("is_pleasant", habit.is_pleasant),
        frequency=data.get("frequency", habit.frequency),
    )
    validate_habit(temp_habit)
