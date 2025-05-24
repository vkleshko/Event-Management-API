from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EventViewSet, EventRegistrationView

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="events")

urlpatterns = [
    path("events/registration/<int:pk>/", EventRegistrationView.as_view(), name="registration"),
]
urlpatterns += router.urls
