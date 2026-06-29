from django.shortcuts import render

# request -> /dashboard -> django -> urls.py -> view -> response


def dashboard_webpage(request, *args, **kwargs):
    return render(request, "dashboard/main.html")
