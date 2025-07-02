from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import (
    RoleChoiceForm, StudentRegisterForm,
    TeacherRegisterForm, ParentRegisterForm, CustomLoginForm
)


class RoleSelectView(View):
    def get(self, request):
        form = RoleChoiceForm()
        return render(request, "accounts/register.html", {"form": form})

    def post(self, request):
        form = RoleChoiceForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]
            return redirect(f"/accounts/register/{role}/")
        return render(request, "accounts/register.html", {"form": form})


class RegisterView(View):
    form_classes = {
        'student': StudentRegisterForm,
        'teacher': TeacherRegisterForm,
        'parent': ParentRegisterForm,
    }

    def get(self, request, role):
        form_class = self.form_classes.get(role)
        if not form_class:
            return redirect("register")
        return render(request, "accounts/register.html", {"form": form_class()})

    def post(self, request, role):
        form_class = self.form_classes.get(role)
        if not form_class:
            return redirect("register")

        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
        return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomLoginForm
    
    
def logout_view(request):
    logout(request)
    return redirect("login")


class DeleteAccountView(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return render(request, "accounts/forms/delete.html", {"user": user})
        return redirect("login")
    
    def post(self, request):
        user = request.user
        if user.is_authenticated:
            user.delete()
            logout(request)
            return redirect("login")
        return redirect("profile")

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        return render(request, "accounts/profile.html")
