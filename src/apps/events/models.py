from django.db import models

from apps.users.models import CustomUser


# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(
        verbose_name="Event organizer",
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name="events"
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="event_registrations"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Event registration"
        verbose_name_plural = "Event registrations"
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.full_name} --> {self.event.title}"
