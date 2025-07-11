from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager
from schoolgroups.models import ClassGroup


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        PARENT = 'parent', 'Parent'
        DIRECTOR = 'director', 'Director'

    username = None
    email = models.EmailField("Email address", unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def is_in_classgroup(self, class_group):
        if self.role != "student":
            return False
        return class_group.students.filter(pk=self.student.pk).exists()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    
    def get_class_group(self):
        if ClassGroup.objects.filter(students=self).exists():
            return ClassGroup.objects.filter(students=self).first()
    
    def __str__(self):
        return self.user.get_full_name()


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    subject = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    children = models.ManyToManyField(Student, related_name='parents')

    def __str__(self):
        return self.user.get_full_name()

