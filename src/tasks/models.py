from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from contacts.models import Contact
from events.models import Event


user = settings.AUTH_USER_MODEL


class Task(models.Model):
    owner = models.ForeignKey(user, on_delete=models.CASCADE, related_name="tasks")
    # user.tasks.all()
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="tasks")
    # contact.tasks.all()
    title = models.CharField(max_length=225)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    events = GenericRelation(Event)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.owner:
            self.owner = self.contact.user
        super().save(*args, **kwargs)
