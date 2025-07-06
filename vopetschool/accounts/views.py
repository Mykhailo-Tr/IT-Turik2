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

@login_required
def home_view(request):
    user = request.user
    now = timezone.now()

    # Актуальні голосування
    votes = Vote.objects.filter(
                Q(start_date__isnull=True, end_date__isnull=True) |
                Q(start_date__lte=now, end_date__isnull=True) |
                Q(start_date__isnull=True, end_date__gte=now) |
                Q(start_date__lte=now, end_date__gte=now)
            )

    if user.role != "director":
        votes = votes.filter(
            Q(level=Vote.Level.SCHOOL) |
            Q(level=Vote.Level.SELECTED, participants=user)
        )

    voted_vote_ids = VoteAnswer.objects.filter(voter=user).values_list("option__vote_id", flat=True)

    # Петиції які ще не набрали 50%
    petitions = Petition.objects.filter(deadline__gte=now)
    active_petitions = []
    for petition in petitions:
        if petition.status != Petition.Status.NEW:
            continue
        if petition.is_active() and petition.remaining_supporters_needed() > 0:

            active_petitions.append([petition, petition.get_voted_percentage()])

    return render(request, "accounts/home.html", {
        "user": user,
        "votes": votes[:5],
        "voted_vote_ids": set(voted_vote_ids),
        "petitions": active_petitions[:5],
    })

class RoleSelectView(View):
    def get(self, request):
        return render(request, "accounts/register.html", {"form": RoleChoiceForm(), "step": "choose"})

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

    def get(self, request, role):
        form_class = self.form_classes.get(role)
        if not form_class:
            return redirect("register")
        return render(request, "accounts/register.html", {"form": form_class(), "step": "form", "role": role})

    def post(self, request, role):
        form_class = self.form_classes.get(role)
        if not form_class:
            return redirect("register")
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")
        return render(request, "accounts/register.html", {"form": form, "step": "form", "role": role})


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
        user = get_object_or_404(User, pk=user_id) if user_id else request.user
        context = {"viewed_user": user}
        if user.role == "student":
            context["class_group"] = user.student.get_class_group()
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


