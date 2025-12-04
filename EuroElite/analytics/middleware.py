from time import time

from .utils import track


class PageViewMiddleware:
    """Middleware para registrar page_view automáticamente con contexto rico.

    Mide duración de la petición y envía un evento "page_view" con datos detallados.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Rutas que NO queremos trackear
        self.excluded_paths = [
            "/static",
            "/analytics",
            "/media",
            "/.well-known",
            "/robots.txt",
            "/favicon.ico",
        ]

    def __call__(self, request):
        # Marcar inicio
        request._analytics_start = time()

        response = self.get_response(request)

        try:
            # Evitar estáticos, endpoints de analytics, etc.
            should_track = not any(request.path.startswith(p) for p in self.excluded_paths)
            
            if should_track:
                duration_ms = int((time() - getattr(request, "_analytics_start", time())) * 1000)
                status_code = getattr(response, "status_code", None)
                
                # Props específicos del page_view
                page_props = {
                    "status_code": status_code,
                    "is_error": status_code and status_code >= 400,
                }
                
                # Si hay error, agregarlo
                if status_code and status_code >= 400:
                    page_props["error_status"] = status_code
                
                track(
                    request,
                    "page_view",
                    duration_ms=duration_ms,
                    **page_props
                )
        except Exception as e:
            # nunca romper la respuesta por analytics
            print(f"[analytics.middleware] error tracking page_view: {e}")

        return response
