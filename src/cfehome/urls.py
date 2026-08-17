"""
URL configuration for cfehome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include

from contacts.views import (
    contact_reassign_view,
    contacts_detail_view,
    contacts_list_view,
)
from dashboard.views import dashboard_webpage, team_leaderboard_view

urlpatterns = [
    path("", dashboard_webpage),
    path(
        "contacts/<int:contact_id>/reassign/",
        contact_reassign_view,
        name="contact-reassign",
    ),
    path("contacts/<int:contact_id>/", contacts_detail_view, name="contact-detail"),
    path("contacts/", contacts_list_view, name="contact-list"),
    path("dashboard/", dashboard_webpage),
    path("team/", team_leaderboard_view, name="team-leaderboard"),
    path("admin/", admin.site.urls),
    path("auth/", include("django_googler.urls.default")),
    path(
        "auth/logout/",
        LogoutView.as_view(next_page="/auth/google/login/"),
        name="logout",
    ),
    path("deals/", include("deals.urls", namespace="deals")),
    path("tasks/", include("tasks.urls", namespace="tasks")),
]
