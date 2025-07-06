from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import CalendarEvent

@login_required
def calendar_view(request):
    """
    Відображення календаря на сторінці.
    """
    return render(request, 'calendarapp/calendar.html')


@login_required
def calendar_events_json(request):
    """
    Повертає список подій у форматі JSON для FullCalendar.
    Події беруться з моделі CalendarEvent та можуть бути пов'язані з Petition або Vote.
    """
    user = request.user
    events = CalendarEvent.objects.filter(user=user)

    data = []
    for e in events:
        # Колір події залежно від типу
        if e.is_deadline and e.related_object:
            if e.content_type.model == 'petition':
                color = '#dc3545'  # червоний для петицій
            elif e.content_type.model == 'vote':
                color = '#0d6efd'  # синій для голосувань
            else:
                color = '#6c757d'  # сірий — інше
        else:
            color = '#198754'  # зелений для користувацьких подій

        data.append({
            'id': e.id,
            'title': e.title,
            'start': e.start.isoformat(),
            'end': e.end.isoformat(),
            'description': e.description,
            'color': color,
        })

    return JsonResponse(data, safe=False)
