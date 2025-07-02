# models.py

from django.db import models
from django.conf import settings
from django.utils import timezone


class Vote(models.Model):
    class Level(models.TextChoices):
        SCHOOL = "school", "Вся школа"
        CLASS = "class", "Конкретний клас"
        TEACHERS = "teachers", "Група вчителів"
        SELECTED = "selected", "Вибрані учасники"

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=Level.choices)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    multiple_choices_allowed = models.BooleanField(default=False)  # можна вибрати кілька варіантів
    has_correct_answer = models.BooleanField(default=False)  # чи це тест (з правильною відповіддю)

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="votes_available", blank=True)

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def __str__(self):
        return self.title


class VoteOption(models.Model):
    vote = models.ForeignKey(Vote, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  # для тестів: чи це правильна відповідь

    def __str__(self):
        return self.text


class VoteAnswer(models.Model):
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    option = models.ForeignKey(VoteOption, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("voter", "option")  
