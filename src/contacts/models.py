from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


# django -> db table -> migration
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, default="")
    email = models.EmailField()
