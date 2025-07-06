from django.urls import path
from .views import ClassGroupListCreateUpdateView, TeacherGroupListCreateUpdateView

urlpatterns = [
    path("manage-classes/", ClassGroupListCreateUpdateView.as_view(), name="manage_classes"),
    path("manage-teacher-groups/", TeacherGroupListCreateUpdateView.as_view(), name="manage_teacher_groups"),
]