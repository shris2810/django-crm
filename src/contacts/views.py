from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required

from events.signals import trigger_event
from .models import Contact
from events import services as events_services


@login_required
def contacts_detail_view(request, contact_id=None):
    user = request.user
    instance = Contact.objects.filter(user=user, id=contact_id).first()
    if instance is None:
        raise Http404("Contact not found")

    trigger_event(instance, is_viewed=True, user=user, request=request)

    analytics = events_services.get_event_analytics(instance)
    context = {"contact": instance, "analytics": analytics}
    return render(request, "contacts/detail.html", context)


@login_required
def contacts_list_view(request):
    user = request.user
    qs = Contact.objects.filter(user=user)
    context = {"object_list": qs}
    return render(request, "contacts/list.html", context)


# reverse_events = instance.events.all()
# "reverse_events" : reverse_events,
