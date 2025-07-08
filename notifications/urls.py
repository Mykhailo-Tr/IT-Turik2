from django.urls import path
from . import views

urlpatterns = [
    path("api/", views.notifications_api, name="notifications_api"),
    path("delete/", views.delete_all_notifications, name="delete_notifications"),
    path("delete-single/", views.delete_notification, name="notification_delete_single"),
]
