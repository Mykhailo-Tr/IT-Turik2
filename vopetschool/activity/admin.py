from django.contrib import admin
from .models import UserActivity

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'related_object_title', 'timestamp')
    list_filter = ('type', 'timestamp')
    search_fields = ('user__email', 'related_object_title')
