from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CalendarEvent

@login_required
def calendar_events_json(request):
    events = CalendarEvent.objects.filter(user=request.user)
    data = []
    for e in events:
        color = "#0d6efd"  # Синій — за замовчуванням

        if e.is_deadline and e.related_object:
            if e.content_type.model == 'petition':
                color = "#dc3545"  # Червоний
            elif e.content_type.model == 'vote':
                color = "#0d6efd"  # Синій

        data.append({
            "id": e.id,
            "title": e.title,
            "start": e.start.isoformat(),
            "end": e.end.isoformat(),
            "color": color,
        })

    return JsonResponse(data, safe=False)
