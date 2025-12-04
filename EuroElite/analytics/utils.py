from .models import Event
from .bq import insert_event_async


def _get_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def track(request, name, **props):
    if not request.session.session_key:
        request.session.save()

    # contexto básico del request
    ctx = {
        "url": request.build_absolute_uri() if hasattr(request, "build_absolute_uri") else request.path,
        "path": request.path,
        "method": request.method,
        "host": request.get_host() if hasattr(request, "get_host") else None,
        "user_agent": request.META.get("HTTP_USER_AGENT"),
        "referrer": request.META.get("HTTP_REFERER") or request.META.get("HTTP_ORIGIN"),
        "ip": _get_ip(request),
        "query": dict(request.GET),
    }

    # mezclar props del llamador (prioritarios)
    merged_props = {**ctx, **(props or {})}

    event = Event.objects.create(
        user_id=(request.user.id if getattr(request, "user", None) and request.user.is_authenticated else None),
        session_id=request.session.session_key,
        name=name,
        props=merged_props,
    )

    # preparar dict para BigQuery (se envía en background)
    event_dict = {
        "id": str(event.id),
        "ts": event.ts.isoformat(),
        "event_time": event.ts.isoformat(),
        "event_date": event.ts.date().isoformat(),
        "user_id": event.user_id,
        "session_id": event.session_id,
        "name": event.name,
        "event_type": event.name,
        "properties": event.props,
    }

    try:
        insert_event_async(event_dict)
    except Exception as e:
        print("[analytics.track] error starting async send to BQ:", e)

    return event
