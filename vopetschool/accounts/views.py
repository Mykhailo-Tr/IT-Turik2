from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import User, ClassGroup, TeacherGroup
from django.forms import modelformset_factory
from petitions.models import Petition
from voting.models import Vote, VoteAnswer
from django.db.models import Q
from django.utils import timezone

from .forms import (
    RoleChoiceForm, StudentRegisterForm, TeacherRegisterForm,
    ParentRegisterForm, DirectorRegisterForm, CustomLoginForm,
    EditProfileForm, ClassGroupCreateForm, TeacherGroupCreateForm,
    TeacherGroupEditForm
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


# ---------- Класи ----------

@method_decorator(login_required, name='dispatch')
class ClassGroupListCreateUpdateView(View):
    def get(self, request):
        if request.user.role != 'director':
            return redirect("profile")

        formset = modelformset_factory(ClassGroup, fields=("name",), extra=0)
        context = {
            "classes": ClassGroup.objects.all(),
            "class_form": ClassGroupCreateForm(prefix="class"),
            "edit_class_formset": formset(queryset=ClassGroup.objects.all(), prefix="edit_class")
        }
        return render(request, "accounts/manage_classes.html", context)

    def post(self, request):
        if request.user.role != 'director':
            return redirect("profile")

        ClassGroupFormSet = modelformset_factory(ClassGroup, fields=("name",), extra=0)

        if "submit_class" in request.POST:
            class_form = ClassGroupCreateForm(request.POST, prefix="class")
            if class_form.is_valid():
                class_form.save()
                messages.success(request, "Клас створено.")
        elif "edit_classes" in request.POST:
            formset = ClassGroupFormSet(request.POST, prefix="edit_class")
            if formset.is_valid():
                formset.save()
                messages.success(request, "Класи оновлено.")
        return redirect("manage_classes")


# ---------- Групи вчителів ----------

@method_decorator(login_required, name='dispatch')
class TeacherGroupListCreateUpdateView(View):
    def get(self, request):
        TeacherGroupFormSet = modelformset_factory(
            TeacherGroup,
            form=TeacherGroupEditForm,  # ✅ Важливо
            extra=0
        )
        context = {
            "groups": TeacherGroup.objects.all(),
            "group_form": TeacherGroupCreateForm(prefix="group"),
            "edit_group_formset": TeacherGroupFormSet(
                queryset=TeacherGroup.objects.all(),
                prefix="edit_group"
            ),
        }
        return render(request, "accounts/manage_teacher_groups.html", context)

    def post(self, request):
        TeacherGroupFormSet = modelformset_factory(
            TeacherGroup,
            form=TeacherGroupEditForm,  # ✅ Важливо
            extra=0
        )

        if "submit_group" in request.POST:
            group_form = TeacherGroupCreateForm(request.POST, prefix="group")
            if group_form.is_valid():
                group_form.save()
                messages.success(request, "Групу вчителів успішно створено.")
            else:
                messages.error(request, "Помилка при створенні групи.")
        elif "edit_groups" in request.POST:
            formset = TeacherGroupFormSet(request.POST, prefix="edit_group")
            if formset.is_valid():
                formset.save()
                messages.success(request, "Групи вчителів оновлено.")
            else:
                messages.error(request, "Помилка при оновленні груп.")
                print(formset.errors)

        return redirect("manage_teacher_groups")
