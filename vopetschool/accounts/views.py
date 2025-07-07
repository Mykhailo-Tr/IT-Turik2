from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from petitions.models import Petition
from voting.models import Vote, VoteAnswer
from .models import User
from .forms import (
    RoleChoiceForm, StudentRegisterForm, TeacherRegisterForm,
    ParentRegisterForm, DirectorRegisterForm, CustomLoginForm,
    EditProfileForm
)

# === 🏠 Home View ===

@login_required
def home_view(request):
    now = timezone.now()
    user = request.user

    # Отримати актуальні голосування
    votes = Vote.objects.filter(
        Q(start_date__isnull=True, end_date__isnull=True) |
        Q(start_date__lte=now, end_date__isnull=True) |
        Q(start_date__isnull=True, end_date__gte=now) |
        Q(start_date__lte=now, end_date__gte=now)
    )

    if user.role != User.Role.DIRECTOR:
        votes = votes.filter(
            Q(level=Vote.Level.SCHOOL) |
            Q(level=Vote.Level.SELECTED, participants=user)
        )

    voted_vote_ids = set(
        VoteAnswer.objects.filter(voter=user).values_list("option__vote_id", flat=True)
    )

    # Петиції які ще актуальні
    petitions_qs = Petition.objects.filter(deadline__gte=now, status=Petition.Status.NEW)
    active_petitions = [
        [petition, petition.get_voted_percentage()]
        for petition in petitions_qs
        if petition.is_active() and petition.remaining_supporters_needed() > 0
    ]

    return render(request, "home.html", {
        "user": user,
        "votes": votes[:5],
        "voted_vote_ids": voted_vote_ids,
        "petitions": active_petitions[:5],
    })


class RoleSelectView(View):
    def get(self, request):
        form = RoleChoiceForm()
        return render(request, "accounts/register.html", {"form": form, "step": "choose"})

    def post(self, request):
        form = RoleChoiceForm(request.POST)
        if form.is_valid():
            return redirect("register_role", role=form.cleaned_data["role"])
        return render(request, "accounts/register.html", {"form": form, "step": "choose"})


class RegisterView(View):
    form_classes = {
        User.Role.STUDENT: StudentRegisterForm,
        User.Role.TEACHER: TeacherRegisterForm,
        User.Role.PARENT: ParentRegisterForm,
        User.Role.DIRECTOR: DirectorRegisterForm,
    }

    def dispatch(self, request, *args, **kwargs):
        role = kwargs.get("role")
        if role not in self.form_classes:
            return redirect("register")
        self.form_class = self.form_classes[role]
        self.role = role
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, role):
        form = self.form_class()
        return render(request, "accounts/register.html", {"form": form, "step": "form", "role": self.role})

    def post(self, request, role):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
        return render(request, "accounts/register.html", {"form": form, "step": "form", "role": self.role})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomLoginForm


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request, user_id=None):
        user_to_view = get_object_or_404(User, pk=user_id) if user_id else request.user

        context = {
            "viewed_user": user_to_view,
            "created_petitions": Petition.objects.filter(creator=user_to_view),
            "created_votes": Vote.objects.filter(creator=user_to_view),
            "supported_petitions": Petition.objects.filter(supporters=user_to_view).exclude(creator=user_to_view),
            "answered_votes": VoteAnswer.objects.filter(voter=user_to_view).select_related("option__vote"),
        }

        if user_to_view.role == User.Role.STUDENT:
            context["class_group"] = user_to_view.student.get_class_group()

        return render(request, "accounts/profile.html", context)

@method_decorator(login_required, name='dispatch')
class EditProfileView(View):
    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, "accounts/forms/edit.html", {"form": form})

    def post(self, request):
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено успішно.")
            return redirect("profile")

        messages.error(request, "Не вдалося оновити профіль. Перевірте форму.")
        return render(request, "accounts/forms/edit.html", {"form": form})


@method_decorator(login_required, name='dispatch')
class DeleteAccountView(View):
    def get(self, request):
        return render(request, "accounts/forms/delete.html", {"user": request.user})

    def post(self, request):
        request.user.delete()
        logout(request)
        messages.success(request, "Ваш акаунт було видалено.")
        return redirect("login")
