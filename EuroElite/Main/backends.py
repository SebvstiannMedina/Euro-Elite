from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from .models import Usuario

class BloqueoBackend(ModelBackend):
    """
    Impide el login de usuarios bloqueados.
    """
    def user_can_authenticate(self, user):
        # Evita login si el usuario está bloqueado
        if getattr(user, 'bloqueado', False):
            return False
        return super().user_can_authenticate(user)
