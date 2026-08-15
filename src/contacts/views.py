from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from events.signals import trigger_event
from .models import Contact
from events import services as events_services
from profiles.decorators import admin_required

User = get_user_model()


@login_required
def contacts_detail_view(request, contact_id=None):
    user = request.user
    is_admin = hasattr(user, "profile") and user.profile.role == "admin"

    if is_admin:
        instance = Contact.objects.filter(id=contact_id).first()
    else:
        instance = Contact.objects.filter(user=user, id=contact_id).first()

    if instance is None:
        raise Http404("Contact not found")

    trigger_event(instance, is_viewed=True, user=user, request=request)

    analytics = events_services.get_event_analytics(
        instance, gapfill=True, ignore_type=["unknown", "created"]
    )

    context = {
        "contact": instance,
        "deals": instance.deals.all() if hasattr(instance, "deals") else [],
        "tasks": instance.tasks.all() if hasattr(instance, "tasks") else [],
        "users": User.objects.all() if is_admin else None,
        "analytics": list(analytics),
    }
    return render(request, "contacts/detail.html", context)


@login_required
def contacts_list_view(request):
    user = request.user

    if hasattr(user, "profile") and user.profile.role == "admin":
        qs = Contact.objects.all()
    else:
        qs = Contact.objects.filter(user=user)

    context = {
        "object_list": qs,
    }
    return render(request, "contacts/list.html", context)


@admin_required
def contact_reassign_view(request, contact_id):
    """
    Admin-only view to reassign a contact to a different user.
    Expects a POST request with 'new_owner_id' in the payload.
    """
    if request.method == "POST":
        contact = get_object_or_404(Contact, id=contact_id)
        new_user_id = request.POST.get("new_owner_id")
        if new_user_id:
            new_owner = get_object_or_404(User, id=new_user_id)
            contact.user = new_owner
            contact.save()

        return redirect(contact.get_absolute_url())

    # If not a POST request, just redirect back to the detail page securely
    contact = get_object_or_404(Contact, id=contact_id)
    return redirect(contact.get_absolute_url())
