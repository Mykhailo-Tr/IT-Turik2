from django.db import models
from django.conf import settings

class UserActivity(models.Model):
    class ActivityType(models.TextChoices):
        CREATED_PETITION = 'created_petition', 'Created Petition'
        SUPPORTED_PETITION = 'supported_petition', 'Supported Petition'
        CREATED_VOTE = 'created_vote', 'Created Vote'
        ANSWERED_VOTE = 'answered_vote', 'Answered Vote'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_log')
    type = models.CharField(max_length=50, choices=ActivityType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional context data
    related_object_title = models.CharField(max_length=255)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    extra_info = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.get_type_display()} at {self.timestamp}"