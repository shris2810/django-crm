from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from profiles.decorators import admin_required

TEMPLATES_DIR = settings.TEMPLATES_DIR


@login_required
def dashboard_webpage(request, *args, **kwargs):
    # Route to the appropriate dashboard based on role
    if hasattr(request.user, "profile") and request.user.profile.role == "admin":
        return admin_dashboard_view(request, *args, **kwargs)

    return sales_rep_dashboard_view(request, *args, **kwargs)


@admin_required
def admin_dashboard_view(request, *args, **kwargs):
    template_context = {
        "role": "Admin",
        "dashboard_title": "Team Dashboard",
    }
    return render(request, "dashboard/main.html", template_context)


@login_required
def sales_rep_dashboard_view(request, *args, **kwargs):
    template_context = {
        "role": "Sales Rep",
        "dashboard_title": "Personal Dashboard",
    }
    return render(request, "dashboard/main.html", template_context)
