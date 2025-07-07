from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from google_auth_oauthlib.flow import Flow
import os
from .models import CalendarEvent
from .google_calendar import SCOPES

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


@login_required
def google_auth_init(request):
    flow = Flow.from_client_secrets_file(os.path.join(settings.BASE_DIR, 'credentials.json'),
        scopes=SCOPES,
        redirect_uri=request.build_absolute_uri('/calendar/oauth2callback/')
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    request.session['flow_state'] = flow.state
    return redirect(auth_url)

@login_required
def google_auth_callback(request):
    flow = Flow.from_client_secrets_file(...)
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    creds = flow.credentials
    os.makedirs(os.path.join(settings.BASE_DIR, 'tokens'), exist_ok=True)
    with open(os.path.join(settings.BASE_DIR, 'tokens', f'{request.user.id}_token.json'), 'w') as f:
        f.write(creds.to_json())
    return redirect('calendar')
