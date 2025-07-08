from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.forms import modelformset_factory
from django.views.decorators.http import require_POST

from accounts.models import Student
from .models import ClassGroup, TeacherGroup
from .forms import (
    ClassGroupCreateForm,
    TeacherGroupCreateForm,
    TeacherGroupEditForm,
)


# ---------------- КЛАСИ ----------------

@login_required
def manage_classes(request):
    if request.user.role != 'director':
        return redirect("profile")

    classes = ClassGroup.objects.all()
    form = ClassGroupCreateForm()
    context = {
        "classes": classes,
        "form": form,
    }
    return render(request, "schoolgroups/manage_classes.html", context)


@login_required
def create_class(request):
    if request.user.role != 'director':
        return redirect("profile")

    if request.method == "POST":
        form = ClassGroupCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Клас успішно створено.")
        else:
            messages.error(request, f"Помилка при створенні класу: {form.errors}")
    return redirect("manage_classes")


@login_required
def edit_class(request, pk):
    if request.user.role != 'director':
        return redirect("profile")

    class_group = get_object_or_404(ClassGroup, pk=pk)

    if request.method == "POST":
        new_name = request.POST.get("name", "").strip()
        if not new_name:
            messages.error(request, "Назва класу не може бути порожньою.")
        else:
            class_group.name = new_name
            class_group.save()
            messages.success(request, f"Назву класу оновлено на «{new_name}».")

    return redirect("manage_classes")


@require_POST
@login_required
def delete_class(request, pk):
    if request.user.role != 'director':
        return redirect("profile")

    class_group = get_object_or_404(ClassGroup, pk=pk)
    name = class_group.name
    class_group.delete()
    messages.success(request, f"Клас «{name}» видалено.")
    return redirect("manage_classes")


# ---------------- ГРУПИ ВЧИТЕЛІВ ----------------

@method_decorator(login_required, name='dispatch')
class TeacherGroupListCreateUpdateView(View):
    def get(self, request):
        if request.user.role != 'director':
            return redirect("profile")

        TeacherGroupFormSet = modelformset_factory(
            TeacherGroup,
            form=TeacherGroupEditForm,
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
        return render(request, "schoolgroups/manage_teacher_groups.html", context)

    def post(self, request):
        if request.user.role != 'director':
            return redirect("profile")

        TeacherGroupFormSet = modelformset_factory(
            TeacherGroup,
            form=TeacherGroupEditForm,
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


@require_POST
@login_required
def delete_group(request, pk):
    if request.user.role != 'director':
        return redirect("profile")

    group = get_object_or_404(TeacherGroup, pk=pk)
    name = group.name
    group.delete()
    messages.success(request, f"Групу «{name}» успішно видалено.")
    return redirect("manage_teacher_groups")
