from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import ClassGroup

class Petition(models.Model):
    class Level(models.TextChoices):
        SCHOOL = "school", "Вся школа"
        CLASS = "class", "Конкретний клас"

    title = models.CharField(max_length=255)
    text = models.TextField()
    deadline = models.DateTimeField()
    level = models.CharField(max_length=10, choices=Level.choices)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, null=True, blank=True)

    supporters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="supported_petitions", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return timezone.now() < self.deadline

    def total_needed_supporters(self):
        from accounts.models import User

        if self.level == self.Level.SCHOOL:
            return (User.objects.filter(role="student").count() // 2) + 1
        elif self.level == self.Level.CLASS and self.class_group:
            return (self.class_group.students.count() // 2) + 1
        return 0

    def is_ready_for_review(self):
        return self.supporters.count() >= self.total_needed_supporters()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]