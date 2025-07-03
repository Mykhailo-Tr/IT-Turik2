from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from .forms import (
    RoleChoiceForm, StudentRegisterForm,
    TeacherRegisterForm, ParentRegisterForm, CustomLoginForm,
    DirectorRegisterForm, EditProfileForm
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
        'director': DirectorRegisterForm,
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
            messages.success(request, "Реєстрація успішна! Вітаємо в системі.")
            return redirect("profile")
        messages.error(request, "Помилка при реєстрації. Перевірте форму.")
        return render(request, "accounts/register.html", {"form": form})


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