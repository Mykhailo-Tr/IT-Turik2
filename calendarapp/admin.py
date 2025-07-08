from django.contrib import admin
from .models import CalendarEvent

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end', 'user', 'is_deadline')
    search_fields = ('title', 'description')
    list_filter = ('is_deadline', 'user')
    date_hierarchy = 'start'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related('related_object')