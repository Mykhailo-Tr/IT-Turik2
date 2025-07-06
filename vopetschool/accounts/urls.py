from django.urls import path
from .views import (
    RoleSelectView, RegisterView, CustomLoginView,
    ProfileView, DeleteAccountView, logout_view,
    EditProfileView,
    ClassGroupListCreateUpdateView,
    TeacherGroupListCreateUpdateView,
    CustomLoginView, ProfileView, 
    DeleteAccountView, logout_view, EditProfileView, home_view
)

urlpatterns = [
    path("", home_view, name="home"),
    path("register/", RoleSelectView.as_view(), name="register"),
    path("accounts/register/<str:role>/", RegisterView.as_view(), name="register_role"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("accounts/delete/", DeleteAccountView.as_view(), name="delete_account"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/<int:user_id>/", ProfileView.as_view(), name="user_profile"),
    path("accounts/edit/", EditProfileView.as_view(), name="edit_profile"),

    path("manage-classes/", ClassGroupListCreateUpdateView.as_view(), name="manage_classes"),
    path("manage-teacher-groups/", TeacherGroupListCreateUpdateView.as_view(), name="manage_teacher_groups"),
]
