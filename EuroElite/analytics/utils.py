from .models import Event

def track(request, name, **props):
    if not request.session.session_key:
        request.session.save()

    Event.objects.create(
        user_id=(request.user.id if request.user.is_authenticated else None),
        session_id=request.session.session_key,
        name=name,
        props=props or {},
    )
