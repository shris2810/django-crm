import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TaskCreateForm
from .models import Task


@login_required
def task_list_view(request):
    user = request.user
    is_admin = hasattr(user, "profile") and user.profile.role == "admin"

    # Admins see all tasks; Sales Reps see only their own.
    # select_related('contact') prevents N+1 queries when rendering each task row.
    if is_admin:
        qs = Task.objects.select_related("contact", "owner").all()
    else:
        qs = Task.objects.select_related("contact", "owner").filter(owner=user)

    # Best Practice: Sort incomplete tasks first, then by due date ascending.
    # Completed tasks sink to the bottom of the list naturally.
    qs = qs.order_by("is_completed", "due_date")

    context = {
        "tasks": qs,
        "is_admin": is_admin,
        # Inject today's date so the template can determine overdue tasks
        # without any Python logic leaking into the template layer.
        "today": datetime.date.today(),
    }
    return render(request, "tasks/list.html", context)


@login_required
def task_create_view(request):
    # Pass request.user to the form so it can filter the contact queryset correctly.
    form = TaskCreateForm(request.POST or None, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            task = form.save(commit=False)
            # Best Practice: Set the owner server-side, never trust the client.
            task.owner = request.user
            task.save()
            return redirect("tasks:list")

    context = {"form": form}
    return render(request, "tasks/create.html", context)


@login_required
@require_POST  # Best Practice: Prevent GET requests from mutating state.
def task_complete_view(request, task_id):
    user = request.user
    is_admin = hasattr(user, "profile") and user.profile.role == "admin"

    # Security: Sales Reps can only complete their own tasks.
    if is_admin:
        task = get_object_or_404(Task, id=task_id)
    else:
        task = get_object_or_404(Task, id=task_id, owner=user)

    task.is_completed = True
    task.save()

    return redirect("tasks:list")
