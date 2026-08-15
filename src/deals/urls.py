from django.urls import path
from .views import deals_list_view, deals_detail_view

app_name = "deals"
urlpatterns = [
    path("", deals_list_view, name="list"),
    path("<int:deal_id>/", deals_detail_view, name="detail"),
]
