
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("accounts.urls")),
    path("votes/", include("voting.urls")),
    path("petitions/", include("petitions.urls")),
    path("notifications/", include("notifications.urls")),
    path("groups/", include("schoolgroups.urls")),
    path('calendar/', include('calendarapp.urls')),
    path('set_language/', set_language, name='set_language'),
    path("i18n/", include("django.conf.urls.i18n")), 


]
