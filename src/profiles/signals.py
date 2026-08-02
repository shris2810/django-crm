from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Profile

user = get_user_model()


@receiver(post_save, sender=user)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = "admin" if user.objects.count() == 1 else "sales_rep"

        Profile.objects.create(
            user=instance,
            role=role,
        )
