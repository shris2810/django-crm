from django import forms
from .models import Task
from contacts.models import Contact


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["contact", "title", "due_date"]
        widgets = {
            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        # We pop the user from kwargs so we can filter the contacts dropdown
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Apply basic Tailwind classes to the remaining fields
        self.fields["title"].widget.attrs.update(
            {
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            }
        )
        self.fields["contact"].widget.attrs.update(
            {
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            }
        )

        if self.user:
            is_admin = (
                hasattr(self.user, "profile") and self.user.profile.role == "admin"
            )
            if not is_admin:
                # Security/Best Practice: Sales Reps can only assign tasks to their own contacts
                self.fields["contact"].queryset = Contact.objects.filter(user=self.user)
