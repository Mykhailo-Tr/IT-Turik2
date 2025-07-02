from django.urls import path
from .views import RoleSelectView, RegisterView, CustomLoginView, ProfileView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("register/", RoleSelectView.as_view(), name="register"),
    path("register/<str:role>/", RegisterView.as_view(), name="register_role"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
