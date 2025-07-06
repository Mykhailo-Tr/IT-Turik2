
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("accounts.urls")),
    path("votes/", include("voting.urls")),
    path("petitions/", include("petitions.urls")),
    path("notifications/", include("notifications.urls")),
    path("groups/", include("schoolgroups.urls")),
]
