from time import time

from .utils import track


class PageViewMiddleware:
    """Middleware para registrar page_view automáticamente.

    Mide duración de la petición y envía un evento "page_view" con datos básicos.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # marcar inicio
        request._analytics_start = time()

        response = self.get_response(request)

        try:
            # evitar estáticos y endpoints de analytics para evitar bucles
            if not request.path.startswith("/static") and not request.path.startswith("/analytics"):
                duration_ms = int((time() - getattr(request, "_analytics_start", time())) * 1000)
                track(request, "page_view",
                      url=request.path,
                      method=request.method,
                      status=getattr(response, "status_code", None),
                      duration_ms=duration_ms,
                      )
        except Exception:
            # nunca romper la respuesta por analytics
            pass

        return response
