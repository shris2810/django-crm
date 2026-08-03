from django.dispatch import receiver
from django.utils import timezone
from events.signals import event_did_trigger

from .models import Event


@receiver(event_did_trigger)
def handle_post_save_signal(
    sender, event_type, content_object, user=None, *args, **kwargs
):
    """Handle the event_did_trigger signal and create an Event instance."""

    # print(sender, event_type, content_object, user)
    Event.objects.create(
        type=event_type, content_object=content_object, user=user, time=timezone.now()
    )
