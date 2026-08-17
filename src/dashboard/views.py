import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.shortcuts import render

from deals.models import Deal
from profiles.decorators import admin_required
from tasks.models import Task


@login_required
def dashboard_webpage(request, *args, **kwargs):
    # Route to the appropriate dashboard based on role.
    # hasattr guard handles new users whose profile may not yet exist.
    if hasattr(request.user, "profile") and request.user.profile.role == "admin":
        return admin_dashboard_view(request, *args, **kwargs)
    return sales_rep_dashboard_view(request, *args, **kwargs)


User = get_user_model()


@admin_required
def admin_dashboard_view(request, *args, **kwargs):
    today = datetime.date.today()
    now = datetime.datetime.now()

    # --- Greeting ---
    hour = now.hour
    if hour < 12:
        greeting_prefix = "Good morning"
    elif hour < 17:
        greeting_prefix = "Good afternoon"
    else:
        greeting_prefix = "Good evening"
    first_name = request.user.first_name or request.user.username
    greeting = f"{greeting_prefix}, {first_name} — here's the team overview"

    # --- Team KPIs ---
    team_pipeline_value = (
        Deal.objects.exclude(stage__in=[Deal.Stage.WON, Deal.Stage.LOST]).aggregate(
            total=Sum("value")
        )["total"]
        or 0
    )
    team_open_deals = Deal.objects.exclude(
        stage__in=[Deal.Stage.WON, Deal.Stage.LOST]
    ).count()

    team_won = Deal.objects.filter(stage=Deal.Stage.WON).count()
    team_closed = Deal.objects.filter(
        stage__in=[Deal.Stage.WON, Deal.Stage.LOST]
    ).count()
    team_win_rate = round((team_won / team_closed) * 100) if team_closed > 0 else 0

    team_overdue_tasks = Task.objects.filter(
        is_completed=False, due_date__lt=today
    ).count()

    # --- Pipeline by Stage (for bars) ---
    stage_data = list(
        Deal.objects.exclude(stage__in=[Deal.Stage.WON, Deal.Stage.LOST])
        .values("stage")
        .annotate(count=Count("id"), total_value=Sum("value"))
        .order_by("stage")
    )
    # Need max value to calculate percentage widths for CSS bars. Must be >= 1 to avoid division by zero
    max_stage_value = max([item["total_value"] or 0 for item in stage_data], default=1)
    if max_stage_value == 0:
        max_stage_value = 1

    for item in stage_data:
        val = item["total_value"] or 0
        width_pct = round((float(val) / float(max_stage_value)) * 100)
        item["bar_style"] = f"background-color: #248F8D; width: {width_pct}%;"

    # --- Urgent Team Tasks ---
    urgent_tasks = (
        Task.objects.filter(is_completed=False)
        .select_related("contact", "owner")
        .order_by("due_date")[:5]
    )

    # --- Recent Closed Deals ---
    recent_closed = (
        Deal.objects.filter(stage__in=[Deal.Stage.WON, Deal.Stage.LOST])
        .select_related("contact", "owner")
        .order_by("-closed_at")[:5]
    )

    context = {
        "dashboard_title": "Team Dashboard",
        "greeting": greeting,
        "today": today,
        "team_pipeline_value": team_pipeline_value,
        "team_open_deals": team_open_deals,
        "team_win_rate": team_win_rate,
        "team_overdue_tasks": team_overdue_tasks,
        "stage_data": stage_data,
        "max_stage_value": max_stage_value,
        "urgent_tasks": urgent_tasks,
        "recent_closed": recent_closed,
    }
    return render(request, "dashboard/admin.html", context)


@admin_required
def team_leaderboard_view(request, *args, **kwargs):
    today = datetime.date.today()

    # --- Leaderboard Data ---
    reps_qs = (
        User.objects.filter(profile__role="sales_rep")
        .annotate(
            open_pipeline=Sum(
                "deals__value",
                filter=~Q(deals__stage__in=[Deal.Stage.WON, Deal.Stage.LOST]),
            ),
            open_deals_count=Count(
                "deals", filter=~Q(deals__stage__in=[Deal.Stage.WON, Deal.Stage.LOST])
            ),
            won_deals=Count("deals", filter=Q(deals__stage=Deal.Stage.WON)),
            closed_deals=Count(
                "deals", filter=Q(deals__stage__in=[Deal.Stage.WON, Deal.Stage.LOST])
            ),
            overdue_task_count=Count(
                "tasks", filter=Q(tasks__is_completed=False, tasks__due_date__lt=today)
            ),
        )
        .order_by("-open_pipeline")  # Sort descending by pipeline value
    )

    # Post-process for win rate and identifying top/bottom performers based on pipeline
    rep_data = []
    for rep in reps_qs:
        win_rate = (
            round((rep.won_deals / rep.closed_deals) * 100)
            if rep.closed_deals > 0
            else 0
        )
        rep_data.append(
            {
                "rep": rep,
                "open_pipeline": rep.open_pipeline or 0,
                "open_deals_count": rep.open_deals_count,
                "win_rate": win_rate,
                "overdue_task_count": rep.overdue_task_count,
            }
        )

    # Mark top/bottom for highlighting
    if rep_data:
        rep_data[0]["is_top"] = True
        if len(rep_data) > 1:
            rep_data[-1]["is_bottom"] = True

    context = {
        "dashboard_title": "Team Leaderboard",
        "rep_data": rep_data,
    }
    return render(request, "dashboard/team.html", context)


@login_required
def sales_rep_dashboard_view(request, *args, **kwargs):
    user = request.user
    today = datetime.date.today()

    # --- Greeting ---
    # Time-aware greeting using the server's local hour.
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting_prefix = "Good morning"
    elif hour < 17:
        greeting_prefix = "Good afternoon"
    else:
        greeting_prefix = "Good evening"
    first_name = user.first_name or user.username
    greeting = f"{greeting_prefix}, {first_name} — here's your pipeline"

    # --- KPI 1: Pipeline Value ---
    # Sum all open (non-closed) deal values. Default to 0 if no deals exist.
    pipeline_value = (
        Deal.objects.filter(owner=user)
        .exclude(stage__in=[Deal.Stage.WON, Deal.Stage.LOST])
        .aggregate(total=Sum("value"))["total"]
        or 0
    )

    # --- KPI 2: Open Deal Count ---
    open_deals_count = (
        Deal.objects.filter(owner=user)
        .exclude(stage__in=[Deal.Stage.WON, Deal.Stage.LOST])
        .count()
    )

    # --- KPI 3: Win Rate ---
    # Two targeted queries instead of one large queryset to keep logic clear.
    won_count = Deal.objects.filter(owner=user, stage=Deal.Stage.WON).count()
    closed_count = Deal.objects.filter(
        owner=user, stage__in=[Deal.Stage.WON, Deal.Stage.LOST]
    ).count()
    win_rate = round((won_count / closed_count) * 100) if closed_count > 0 else 0

    # --- KPI 4: Overdue Task Count ---
    overdue_tasks_count = Task.objects.filter(
        owner=user, is_completed=False, due_date__lt=today
    ).count()

    # --- Urgent Tasks (incomplete, nearest due date first, max 5) ---
    # select_related prevents N+1 queries when the template accesses task.contact.
    urgent_tasks = (
        Task.objects.filter(owner=user, is_completed=False)
        .select_related("contact")
        .order_by("due_date")[:5]
    )

    # --- Recent Deals (newest first, max 5) ---
    recent_deals = (
        Deal.objects.filter(owner=user)
        .select_related("contact")
        .order_by("-created_at")[:5]
    )

    context = {
        "dashboard_title": "My Dashboard",
        "greeting": greeting,
        "today": today,
        # KPIs
        "pipeline_value": pipeline_value,
        "open_deals_count": open_deals_count,
        "win_rate": win_rate,
        "overdue_tasks_count": overdue_tasks_count,
        # Sections
        "urgent_tasks": urgent_tasks,
        "recent_deals": recent_deals,
    }
    return render(request, "dashboard/sales_rep.html", context)
