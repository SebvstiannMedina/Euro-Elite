import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .utils import track


@csrf_exempt
@require_POST
def track_event(request):
	"""Endpoint público para recibir eventos desde frontend o backend.

	Cuerpo esperado:
	{"name": "event_name", "props": { ... }}
	"""
	try:
		data = json.loads(request.body.decode("utf-8") or "{}")
	except Exception as e:
		print(f"[analytics.track_event] invalid json: {e}")
		return HttpResponseBadRequest(json.dumps({"error": "invalid json"}), content_type="application/json")

	name = data.get("name")
	props = data.get("props") or {}

	if not name:
		return HttpResponseBadRequest(json.dumps({"error": "missing event name"}), content_type="application/json")

	if not isinstance(name, str) or len(name) > 100:
		return HttpResponseBadRequest(json.dumps({"error": "invalid event name"}), content_type="application/json")

	if not isinstance(props, dict):
		props = {}

	try:
		track(request, name, **props)
	except Exception as e:
		print(f"[analytics.track_event] error tracking event '{name}': {e}")

	return JsonResponse({"ok": True})


def health(request):
	return JsonResponse({"ok": True, "service": "analytics"})
