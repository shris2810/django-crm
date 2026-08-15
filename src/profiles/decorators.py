# profiles/decorators.py
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    Restrict a view to users whose profile.role is one of allowed_roles.

    - Unauthenticated users -> redirected to login, with ?next= back to
      the page they requested.
    - Authenticated users with no profile, or the wrong role -> 403
      (PermissionDenied), handled by Django's standard 403 error page.

    Usage:
        @role_required("admin")
        def team_dashboard(request): ...

        @role_required("admin", "sales_rep")   # either role allowed
        def shared_view(request): ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            profile = getattr(request.user, "profile", None)
            if profile is not None and profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied(
                f"This page requires one of these roles: {', '.join(allowed_roles)}."
            )

        return _wrapped_view

    return decorator


# Convenience aliases — cover the two roles that exist today
admin_required = role_required("admin")
sales_rep_required = role_required("sales_rep")
