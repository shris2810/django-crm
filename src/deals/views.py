from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Deal
from .forms import DealStageForm


@login_required
def deals_list_view(request):
    user = request.user
    is_admin = hasattr(user, "profile") and user.profile.role == "admin"

    if is_admin:
        qs = (
            Deal.objects.select_related("contact", "owner")
            .all()
            .order_by("-expected_close_date")
        )
    else:
        qs = (
            Deal.objects.select_related("contact", "owner")
            .filter(owner=user)
            .order_by("-expected_close_date")
        )

    context = {"deals": qs, "is_admin": is_admin}
    return render(request, "deals/list.html", context)


@login_required
def deals_detail_view(request, deal_id=None):
    user = request.user
    is_admin = hasattr(user, "profile") and user.profile.role == "admin"

    if is_admin:
        instance = get_object_or_404(
            Deal.objects.select_related("contact", "owner"), id=deal_id
        )
    else:
        instance = get_object_or_404(
            Deal.objects.select_related("contact", "owner"), id=deal_id, owner=user
        )

    form = DealStageForm(request.POST or None, instance=instance)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("deals:detail", deal_id=instance.id)

    context = {
        "deal": instance,
        "form": form,
        "is_admin": is_admin,
    }
    return render(request, "deals/detail.html", context)
