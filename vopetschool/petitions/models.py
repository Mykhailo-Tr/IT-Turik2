from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import ClassGroup, User


class Petition(models.Model):
    class Level(models.TextChoices):
        SCHOOL = "school", "Вся школа"
        CLASS = "class", "Конкретний клас"
        
    class Status(models.TextChoices):
        NEW = "new", "Нова"
        PENDING = "pending", "Очікує на розгляд"
        APPROVED = "approved", "Затверджено"
        REJECTED = "rejected", "Відхилено"

    title = models.CharField(max_length=255)
    text = models.TextField()
    deadline = models.DateTimeField()
    level = models.CharField(max_length=10, choices=Level.choices)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, null=True, blank=True)

    supporters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="supported_petitions", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)

    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_petitions")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return timezone.now() < self.deadline

    def total_needed_supporters(self):
        if self.level == self.Level.SCHOOL:
            return (User.objects.filter(role="student").count() // 2) 
        elif self.level == self.Level.CLASS and self.class_group:
            return (self.class_group.students.count() // 2) 
        return 0
    
    def remaining_supporters_needed(self):
        return max(self.total_needed_supporters() - self.supporters.count(), 0)

    def get_eligible_voters_count(self):
        if self.level == self.Level.SCHOOL:
            return User.objects.filter(role="student").count()
        elif self.level == self.Level.CLASS and self.class_group:
            return self.class_group.students.count()
        return 0

    def is_ready_for_review(self):
        print(f"Supporters count: {self.supporters.count()}, Total needed: {self.total_needed_supporters()}")
        return self.supporters.count() > self.total_needed_supporters()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    petition = models.ForeignKey(Petition, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def was_edited(self):
        return self.updated_at and self.created_at < self.updated_at

    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.petition.title}"
    
    