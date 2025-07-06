from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'link', 'created_at')
    search_fields = ('user__email', 'message')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False
