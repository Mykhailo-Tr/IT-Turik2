from django.db import models


class TeacherGroup(models.Model):
    name = models.CharField(max_length=100)
    teachers = models.ManyToManyField("accounts.Teacher", related_name="groups", blank=True)

    def __str__(self):
        return self.name


class ClassGroup(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField("accounts.Student", related_name="class_groups", blank=True)

    def __str__(self):
        return self.name
