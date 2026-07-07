from random import randint

from django.conf import settings
from django.shortcuts import redirect, render

TEMPLATES_DIR = settings.TEMPLATES_DIR
print("TEMPLATES_DIR", TEMPLATES_DIR, TEMPLATES_DIR.exists())


# request -> /dashboard -> django -> urls.py -> view -> response


def dashboard_webpage(request, *args, **kwargs):
    print(request.user, request.user.is_authenticated)
    if not request.user.is_authenticated:
        return redirect("/auth/google/login/")
    my_value = str(request.user) + f"{randint(0, 129039109202)}"
    template_context = {
        "my_value": my_value,
        "not_actual_context": "now it's ready",
        "colors": ["red", "blue"],
    }
    return render(request, "dashboard/main.html", template_context)
