from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from contacts.models import Contact
from django.conf import settings

from events.models import Event

user = settings.AUTH_USER_MODEL


class Deal(models.Model):
    class Stage(models.TextChoices):
        NEW = "new", "New"
        CONTACT_MADE = "contact_made", "Contact Made"
        PROPOSAL_SENT = "proposal_sent", "Proposal Sent"
        NEGOTIATION = "negotiation", "Negotiation"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    class LostReason(models.TextChoices):
        BUDGET = "budget", "Out of Budget"
        COMPETITOR = "competitor", "Competitor"
        NO_RESPONSE = "no_response", "No Response"
        TIMING = "timing", "Bad Timing"
        OTHER = "other", "Other"

    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="deals"
    )  # contact.deals.all()

    owner = models.ForeignKey(
        user, on_delete=models.CASCADE, related_name="deals"
    )  # user.deals.all()

    value = models.DecimalField(max_digits=10, decimal_places=2)
    expected_close_date = models.DateField()

    stage = models.CharField(
        max_length=20, choices=Stage.choices, default=Stage.NEW, db_index=True
    )
    lost_reason = models.CharField(
        max_length=20,
        choices=LostReason.choices,
        default=LostReason.OTHER,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    events = GenericRelation(Event)

    def save(self, *args, **kwargs):
        if self.stage in (self.Stage.WON, self.Stage.LOST):
            if self.closed_at is None:
                self.closed_at = timezone.now()
        else:
            # closed_at will be not None only when deal marked as won or lost
            self.closed_at = None
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/deals/{self.id}/"
