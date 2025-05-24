import django_filters
from drf_yasg import openapi
from rest_framework import status
from rest_framework import filters
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

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

    @swagger_auto_schema(
        operation_summary="List all events",
        operation_description=(
                "Returns a list of events. "
                "Supports filtering by date range (`date_from`, `date_to`) and `location`, "
                "as well as search by `title` and `description`."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Search by title or description",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name="date_from",
                in_=openapi.IN_QUERY,
                description="Filter events from this date (inclusive) — format YYYY-MM-DD",
                type=openapi.TYPE_STRING,
                format="date"
            ),
            openapi.Parameter(
                name="date_to",
                in_=openapi.IN_QUERY,
                description="Filter events up to this date (inclusive) — format YYYY-MM-DD",
                type=openapi.TYPE_STRING,
                format="date"
            ),
            openapi.Parameter(
                name="location",
                in_=openapi.IN_QUERY,
                description="Filter by exact location (case-insensitive)",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Get event by ID",
        operation_description="Retrieve details of a specific event by its ID."
    )
    def retrieve(self, request, pk=None):
        event = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(event, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create new event",
        operation_description="Authenticated users can create a new event by providing event data."
    )
    def create(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication is required to create an event."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Update event partially",
        operation_description="Authenticated users can update an event they created (partial update)."
    )
    def partial_update(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication is required to edit an event."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if event.organizer != request.user:
            return Response(
                {"error": "You do not have permission to edit this event."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance=event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Delete event",
        operation_description="Authenticated users can delete an event they created."
    )
    def destroy(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication is required to delete an event."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if event.organizer != request.user:
            return Response(
                {"error": "You do not have permission to delete this event."},
                status=status.HTTP_403_FORBIDDEN
            )

        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventRegistrationView(APIView):
    @swagger_auto_schema(
        operation_summary="Register for an event",
        operation_description=(
                "Allows an authenticated user to register for a specific event by its ID. "
                "If registration is successful, a confirmation email will be sent to the user. "
        ),
    )
    def post(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication is required to register on event."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        event = get_object_or_404(Event, pk=pk)

        try:
            registered_event = EventRegistration.objects.create(
                user=request.user,
                event=event
            )

        except IntegrityError:
            return Response(
                {"error": f"You are already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            send_email_after_event_registration(user=request.user, event=event)
        except Exception as e:
            print(f"Email sending failed: {e}")

        serializer = EventRegistrationSerializer(instance=registered_event, many=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
