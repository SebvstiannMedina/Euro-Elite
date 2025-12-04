import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .utils import track


@csrf_exempt
@require_POST
def track_event(request):
	"""Endpoint público (POST JSON) para recibir eventos desde frontend.

	Cuerpo esperado: {"name": "event_name", "props": {...}}
	"""
	try:
		data = json.loads(request.body.decode("utf-8") or "{}")
	except Exception:
		return HttpResponseBadRequest("invalid json")

	name = data.get("name")
	props = data.get("props") or {}

	if not name:
		return HttpResponseBadRequest("missing event name")

	try:
		track(request, name, **props)
	except Exception as e:
		# no romper la experiencia frontend
		print("[analytics.track_event] error tracking:", e)

	return JsonResponse({"ok": True})


def health(request):
	return JsonResponse({"ok": True})
