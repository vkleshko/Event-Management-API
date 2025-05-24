from rest_framework import serializers

from .models import Event, EventRegistration


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.CharField(source="organizer.full_name", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "location",
            "organizer",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        organizer = request.user
        return Event.objects.create(**validated_data, organizer=organizer)


class EventRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.full_name", read_only=True)
    event = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = EventRegistration
        fields = ["id", "event", "user"]
