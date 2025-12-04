from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    
    def ready(self):
        # conectar signals para login/logout
        try:
            from . import signals  # noqa
        except Exception:
            pass
