import django_filters
from drf_yasg import openapi
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters, generics, permissions

from .models import Event, EventRegistration
from .utils import send_email_after_event_registration
from .serializers import EventSerializer, EventRegistrationSerializer


class EventFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Event
        fields = {"location": ["iexact"]}


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ["title", "description"]

    def get_permissions(self):
        if self.action in ["create", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated()]
        return []

    @swagger_auto_schema(
        operation_summary="List all events",
        operation_description=(
                "Returns a list of events. "
                "Supports filtering by date range (`date_from`, `date_to`) and `location`, "
                "as well as search by `title` and `description`."
        ),
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search by title or description",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "date_from",
                openapi.IN_QUERY,
                description="Start date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format="date"
            ),
            openapi.Parameter(
                "date_to",
                openapi.IN_QUERY,
                description="End date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format="date"
            ),
            openapi.Parameter(
                "location",
                openapi.IN_QUERY,
                description="Exact location (case-insensitive)",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        operation_summary="Retrieve event by ID",
        operation_description="Retrieve a single event by ID."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new event",
        operation_description="Create a new event. Only authenticated users can create events."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @swagger_auto_schema(
        operation_summary="Partially update event",
        operation_description="Only the organizer can update an event."
    )
    def partial_update(self, request, *args, **kwargs):
        event = self.get_object()
        if event.organizer != request.user:
            return Response(
                {"error": "You do not have permission to edit this event."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete event",
        operation_description="Only the organizer can delete an event."
    )
    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        if event.organizer != request.user:
            return Response(
                {"error": "You do not have permission to delete this event."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class EventRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Register for an event",
        operation_description="Authenticated users can register for an event by its ID."
    )
    def post(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)

        try:
            registered_event = EventRegistration.objects.create(
                user=request.user, event=event
            )
        except IntegrityError:
            return Response(
                {"error": "You are already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            send_email_after_event_registration(user=request.user, event=event)
        except Exception as e:
            print(f"Email sending failed: {e}")

        serializer = EventRegistrationSerializer(registered_event)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
