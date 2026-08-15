from django.urls import path

from .views import task_list_view, task_create_view, task_complete_view

app_name = "tasks"

urlpatterns = [
    path("", task_list_view, name="list"),
    path("create/", task_create_view, name="create"),
    path("<int:task_id>/complete/", task_complete_view, name="complete"),
]
