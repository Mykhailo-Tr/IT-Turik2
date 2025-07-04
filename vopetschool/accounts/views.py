from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout

from .forms import (
    RoleChoiceForm, StudentRegisterForm,
    TeacherRegisterForm, ParentRegisterForm,
    DirectorRegisterForm, CustomLoginForm,
    EditProfileForm
)
from .models import User


class RoleSelectView(View):
    """Перший крок реєстрації — вибір ролі"""
    def get(self, request):
        form = RoleChoiceForm()
        return render(request, "accounts/register.html", {"form": form, "step": "choose"})

    def post(self, request):
        form = RoleChoiceForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]
            return redirect("register_role", role=role)
        return render(request, "accounts/register.html", {"form": form, "step": "choose"})


class RegisterView(View):
    """Другий крок — форма реєстрації для обраної ролі"""
    form_classes = {
        User.Role.STUDENT: StudentRegisterForm,
        User.Role.TEACHER: TeacherRegisterForm,
        User.Role.PARENT: ParentRegisterForm,
        User.Role.DIRECTOR: DirectorRegisterForm,
    }

    def get(self, request, role):
        form_class = self.form_classes.get(role)
        if not form_class:
            messages.error(request, "Невідома роль.")
            return redirect("register")
        form = form_class()
        return render(request, "accounts/register.html", {"form": form, "step": "form", "role": role})

    def post(self, request, role):
        form_class = self.form_classes.get(role)
        if not form_class:
            messages.error(request, "Невідома роль.")
            return redirect("register")

        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "✅ Реєстрація успішна! Вітаємо в системі.")
            return redirect("profile")
        messages.error(request, "❌ Помилка при реєстрації. Перевірте введені дані.")
        return render(request, "accounts/register.html", {"form": form, "step": "form", "role": role})

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomLoginForm

    def form_valid(self, form):
        messages.success(self.request, "Вхід виконано успішно.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Невірні дані для входу. Спробуйте ще раз.")
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.info(request, "Ви вийшли з системи.")
    return redirect("login")


class DeleteAccountView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, "accounts/forms/delete.html", {"user": request.user})
        return redirect("login")

    def post(self, request):
        if request.user.is_authenticated:
            request.user.delete()
            logout(request)
            messages.success(request, "Ваш акаунт було видалено.")
            return redirect("login")
        return redirect("profile")


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        return render(request, "accounts/profile.html")


class EditProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, "accounts/forms/edit.html", {"form": form})

    @method_decorator(login_required)
    def post(self, request):
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено успішно.")
            return redirect("profile")
        messages.error(request, "Не вдалося оновити профіль. Перевірте форму.")
        return render(request, "accounts/forms/edit.html", {"form": form})