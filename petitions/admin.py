from django.contrib import admin
from .models import Petition, Comment
@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "level", "deadline", "created_at", "is_active", "is_ready_for_review")
    list_filter = ("level", "creator", "created_at")
    search_fields = ("title", "text")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True

    def is_ready_for_review(self, obj):
        return obj.is_ready_for_review()
    is_ready_for_review.boolean = True
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("petition", "author", "created_at", "updated_at")
    list_filter = ("petition", "author", "created_at")
    search_fields = ("text",)
    date_hierarchy = "created_at"
    ordering = ("-updated_at", "-created_at")
