import json
import base64
from django.utils import timezone
from .models import Event
from .bq import insert_event_async


def _get_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _parse_user_agent(ua):
    ua = ua or ""
    lower = ua.lower()
    result = {
        "raw": ua,
        "is_mobile": any(x in lower for x in ["mobile", "android", "iphone", "ipad"]),
        "is_bot": any(x in lower for x in ["bot", "crawler", "spider", "googlebot"]),
    }
    if "chrome" in lower:
        result["browser"] = "Chrome"
    elif "safari" in lower and "chrome" not in lower:
        result["browser"] = "Safari"
    elif "firefox" in lower:
        result["browser"] = "Firefox"
    elif "edge" in lower:
        result["browser"] = "Edge"
    else:
        result["browser"] = "Other"

    if "windows" in lower:
        result["os"] = "Windows"
    elif "mac" in lower:
        result["os"] = "macOS"
    elif "linux" in lower:
        result["os"] = "Linux"
    elif "android" in lower:
        result["os"] = "Android"
    elif "iphone" in lower or "ipad" in lower:
        result["os"] = "iOS"
    else:
        result["os"] = "Other"

    return result


def _extract_request_context(request):
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    ua_parsed = _parse_user_agent(user_agent)

    return {
        "url": request.build_absolute_uri() if hasattr(request, "build_absolute_uri") else request.path,
        "path": request.path,
        "method": request.method,
        "host": request.get_host() if hasattr(request, "get_host") else None,
        "scheme": getattr(request, "scheme", None),
        "user_agent": user_agent,
        "user_agent_parsed": ua_parsed,
        "referrer": request.META.get("HTTP_REFERER") or request.META.get("HTTP_ORIGIN"),
        "ip": _get_ip(request),
        "query_params": dict(request.GET) if request.GET else {},
        "content_type": request.META.get("CONTENT_TYPE"),
        "accept_language": request.META.get("HTTP_ACCEPT_LANGUAGE"),
        "accept_encoding": request.META.get("HTTP_ACCEPT_ENCODING"),
    }


def _extract_user_context(request):
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return {"is_authenticated": False, "user_id": None}

    return {
        "is_authenticated": True,
        "user_id": user.id,
        "username": getattr(user, "username", None),
        "email": getattr(user, "email", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "is_staff": getattr(user, "is_staff", False),
        "is_superuser": getattr(user, "is_superuser", False),
        "date_joined": str(getattr(user, "date_joined", None)) if hasattr(user, "date_joined") else None,
        "last_login": str(getattr(user, "last_login", None)) if hasattr(user, "last_login") else None,
    }


def _extract_session_context(request):
    if not request.session.session_key:
        request.session.save()
    # optional session start time
    if "_session_start_time" not in request.session:
        request.session["_session_start_time"] = timezone.now().isoformat()

    return {
        "session_id": request.session.session_key,
        "session_create_date": str(request.session.get("_session_start_time", timezone.now().isoformat())),
    }


def track(request, name, duration_ms=None, error=None, **props):
    # Extraer contextos
    request_context = _extract_request_context(request)
    user_context = _extract_user_context(request)
    session_context = _extract_session_context(request)

    merged_props = {
        "request": request_context,
        "user": user_context,
        "session": session_context,
        "duration_ms": duration_ms,
        "error": error,
        "timestamp": timezone.now().isoformat(),
        **(props or {}),
    }

    # Guardar en DB local
    user_id = user_context.get("user_id") if user_context.get("is_authenticated") else None
    session_id = session_context.get("session_id")

    event = Event.objects.create(
        user_id=user_id,
        session_id=session_id,
        name=name,
        props=merged_props,
    )

    event_dict = {
        "name": event.name,
        "ts": event.ts.isoformat(),
        "user_id": user_id,
        "session_id": session_id,
        "event_type": name,
        "properties": merged_props,
    }

    try:
        insert_event_async(event_dict)
    except Exception as e:
        print("[analytics.track] error starting async send to BQ:", e)

    return event
