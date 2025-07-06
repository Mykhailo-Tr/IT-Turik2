# notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("api/", views.notifications_api, name="notifications_api"),
    path("delete/", views.delete_notifications, name="delete_notifications"),
]
