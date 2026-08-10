from django.dispatch import receiver
from django.db.models.signals import post_save

from events.signals import trigger_event

from .models import Task


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, *args, **kwargs):
    is_created = created
    is_updated = not created
    trigger_event(
        instance,
        is_created=is_created,
        is_updated=is_updated,
    )
