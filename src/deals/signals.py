from django.dispatch import receiver
from django.db.models.signals import post_save

from events.signals import trigger_event

from .models import Deal


@receiver(post_save, sender=Deal)
def deal_post_save(sender, instance, created, *args, **kwargs):
    is_created = created
    is_updated = not created
    trigger_event(
        instance,
        is_created=is_created,
        is_updated=is_updated,
    )


@receiver(post_save, sender=Deal)
def update_contact_status_on_won(sender, instance, *args, **kwargs):
    if instance.stage == Deal.Stage.WON:
        contact = instance.contact
        contact.status = contact.ContactStatus.CUSTOMER
        contact.save(update_fields=["status"])
