from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('events/', views.calendar_events_json, name='calendar_events_json'),
    path('auth/', views.google_auth_init, name='google_auth'),
    path('oauth2callback/', views.google_auth_callback, name='google_auth_callback'),
]
