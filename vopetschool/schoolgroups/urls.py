from django.urls import path
from .views import ClassGroupListCreateUpdateView, TeacherGroupListCreateUpdateView, edit_class

urlpatterns = [
    path("manage-classes/", ClassGroupListCreateUpdateView.as_view(), name="manage_classes"),
    path("manage-teacher-groups/", TeacherGroupListCreateUpdateView.as_view(), name="manage_teacher_groups"),
    path("edit-class/<int:pk>/", edit_class, name="edit_class"),
]