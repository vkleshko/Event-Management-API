from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.CharField(source='organizer.full_name', read_only=True)

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
