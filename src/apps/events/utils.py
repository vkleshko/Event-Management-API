from django.conf import settings
from django.core.mail import send_mail


def send_email_after_event_registration(user, event):
    send_mail(
        subject=f"Registration Confirmation for Event: {event.title}",
        message=(
            f"Hello, {user.full_name}!\n\n"
            f"Your registration for the event \"{event.title}\" scheduled on {event.date.strftime('%B %d, %Y')} has been successfully confirmed.\n"
            f"Location: {event.location}\n\n"
            f"Thank you for joining us! We look forward to seeing you there.\n\n"
            "Best regards,\n"
            "The Event Management Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
