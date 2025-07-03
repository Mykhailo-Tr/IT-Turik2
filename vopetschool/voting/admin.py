from django.contrib import admin

from django.contrib import admin
from .models import Vote, VoteOption, VoteAnswer


class VoteOptionInline(admin.TabularInline):
    model = VoteOption
    extra = 1


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "level", "is_active", "get_status_display", "start_date", "end_date")
    list_filter = ("level", "start_date", "end_date", "multiple_choices_allowed", "has_correct_answer")
    search_fields = ("title", "description", "creator__username")
    filter_horizontal = ("participants", "teacher_groups", "class_groups")
    inlines = [VoteOptionInline]
    readonly_fields = ("is_active", "get_status_display")


@admin.register(VoteAnswer)
class VoteAnswerAdmin(admin.ModelAdmin):
    list_display = ("voter", "option", "vote_title", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("voter__username", "option__text", "option__vote__title")

    def vote_title(self, obj):
        return obj.option.vote.title
    vote_title.short_description = "Голосування"

@admin.register(VoteOption)
class VoteOptionAdmin(admin.ModelAdmin):
    list_display = ("text", "vote", "is_correct")
    list_filter = ("is_correct", "vote")
    search_fields = ("text", "vote__title")
