from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
from django.db import models

from events.models import Event

User = settings.AUTH_USER_MODEL


# user.modelname_set.all() -> Return every Contact whose user field points to this User
# django -> db table -> migration
class Contact(models.Model):
    class ContactStatus(models.TextChoices):
        LEAD = "lead", "Lead"
        CUSTOMER = "customer", "Customer"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mycontacts"
    )  # user.my_contacts.all()

    first_name = models.CharField(max_length=120, default="", blank=True)
    last_name = models.CharField(max_length=120, default="", blank=True)
    email = models.EmailField(db_index=True)

    phone = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=120, blank=True, null=True)
    source = models.CharField(max_length=120, blank=True, null=True)

    status = models.CharField(
        max_length=20, choices=ContactStatus.choices, default=ContactStatus.LEAD
    )

    notes = models.TextField(blank=True, default="")

    last_edited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="my_contact_edits"
    )  # user.my_contact_edits.all()
    last_sync = models.DateTimeField(
        auto_now_add=False, auto_now=False, blank=True, null=True
    )

    events = GenericRelation(Event)  # contact_instance.events.all()

    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return f"/contacts/{self.id}/"  # type: ignore
