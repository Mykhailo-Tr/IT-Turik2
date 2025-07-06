from django.urls import path
from .views import TeacherGroupListCreateUpdateView
from . import views

urlpatterns = [
    path("manage-teacher-groups/", TeacherGroupListCreateUpdateView.as_view(), name="manage_teacher_groups"),
    path("manage-classes/", views.manage_classes, name="manage_classes"),
    path("create-class/", views.create_class, name="create_class"),
    path("edit-class/<int:pk>/", views.edit_class, name="edit_class"),
    path("delete-class/<int:pk>/", views.delete_class, name="delete_class"),
]
