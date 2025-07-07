from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import CalendarEvent

@login_required
def calendar_view(request):
    return render(request, 'calendarapp/calendar.html')


@login_required
def calendar_events_json(request):
    user = request.user
    events = CalendarEvent.objects.filter(user=user)

    data = []
    for e in events:
        if not e.start or not e.end:
            continue

        if e.is_deadline and e.related_object:
            if e.content_type and e.content_type.model == 'petition':
                color = '#dc3545'  
            elif e.content_type and e.content_type.model == 'vote':
                color = '#0d6efd'  
            else:
                color = '#6c757d'
        else:
            color = '#198754' 

        data.append({
            'id': e.id,
            'title': e.title,
            'start': e.start.isoformat(),
            'end': e.end.isoformat(),
            'description': e.description,
            'color': color,
        })

    return JsonResponse(data, safe=False)

