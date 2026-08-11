from rest_framework import serializers
from .models import Habit, Place
from .validators import validate_habit


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('id', 'name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Название места должно содержать минимум 2 символа')
        return value.strip()


class HabitSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    place_name = serializers.CharField(source='place.name', read_only=True)
    linked_habit_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Habit
        fields = (
            'id', 'owner', 'place', 'place_name', 'action', 'time',
            'is_pleasant', 'linked_habit', 'linked_habit_details', 'frequency',
            'reward', 'time_to_complete', 'is_public', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')

    def get_linked_habit_details(self, obj):
        if obj.linked_habit:
            return {
                'id': obj.linked_habit.id,
                'action': obj.linked_habit.action,
                'is_pleasant': obj.linked_habit.is_pleasant
            }
        return None

    def validate(self, data):
        # Проверяем, что мы не пытаемся установить связанную привычку для приятной
        is_pleasant = data.get('is_pleasant', self.instance.is_pleasant if self.instance else False)
        linked_habit = data.get('linked_habit', self.instance.linked_habit if self.instance else None)
        reward = data.get('reward', self.instance.reward if self.instance else None)
        time_to_complete = data.get('time_to_complete', self.instance.time_to_complete if self.instance else 60)
        frequency = data.get('frequency', self.instance.frequency if self.instance else 1)
        place = data.get('place', self.instance.place if self.instance else None)

        # Создаем временный объект для валидации
        temp_habit = Habit(
            is_pleasant=is_pleasant,
            linked_habit=linked_habit,
            reward=reward,
            time_to_complete=time_to_complete,
            frequency=frequency,
            place=place
        )

        try:
            validate_habit(temp_habit)
        except Exception as e:
            raise serializers.ValidationError(e.message_dict)

        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class HabitPublicSerializer(HabitSerializer):
    class Meta(HabitSerializer.Meta):
        read_only_fields = HabitSerializer.Meta.read_only_fields + ('is_public',)
