from django.contrib.auth.signals import user_logged_in, user_logged_out

from .utils import track


def _on_login(sender, request, user, **kwargs):
    try:
        track(request, "user_login", method="password", user_id=user.id)
    except Exception:
        pass


def _on_logout(sender, request, user, **kwargs):
    try:
        track(request, "user_logout", user_id=(user.id if user else None))
    except Exception:
        pass


user_logged_in.connect(_on_login)
user_logged_out.connect(_on_logout)
