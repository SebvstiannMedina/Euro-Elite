from .models import Event
from .bq import insert_event


def track(request, name, **props):
    if not request.session.session_key:
        request.session.save()

    event = Event.objects.create(
        user_id=(request.user.id if request.user.is_authenticated else None),
        session_id=request.session.session_key,
        name=name,
        props=props or {},
    )

    # preparar dict para BigQuery (síncrono en este ejemplo)
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

    # Enviar a BigQuery (si falla, no interrumpe la creación en la DB local)
    try:
        insert_event(event_dict)
    except Exception as e:
        print("[analytics.track] error sending to BQ:", e)

    return event
