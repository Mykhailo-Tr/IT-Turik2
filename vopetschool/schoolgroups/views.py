from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.forms import modelformset_factory

from accounts.models import Student
from .models import ClassGroup, TeacherGroup
from .forms import (
    ClassGroupCreateForm,
    TeacherGroupCreateForm,
    TeacherGroupEditForm,
)


# ---------- КЛАСИ ----------

@method_decorator(login_required, name='dispatch')
class ClassGroupListCreateUpdateView(View):
    def get(self, request):
        if request.user.role != 'director':
            return redirect("profile")

        context = {
            "classes": ClassGroup.objects.all(),
            "class_form": ClassGroupCreateForm(prefix="class"),
            "all_students": Student.objects.select_related("user").all(),
        }
        return render(request, "schoolgroups/manage_classes.html", context)

    def post(self, request):
        if request.user.role != 'director':
            return redirect("profile")

        class_form = ClassGroupCreateForm(request.POST, prefix="class")
        if class_form.is_valid():
            class_form.save()
            messages.success(request, "Клас успішно створено.")
        else:
            messages.error(request, "Помилка при створенні класу.")
        return redirect("manage_classes")


@login_required
def edit_class(request, pk):
    class_group = get_object_or_404(ClassGroup, pk=pk)

    if request.user.role != 'director':
        return redirect("profile")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        student_ids_raw = request.POST.getlist("students")
        student_ids = [int(sid) for sid in student_ids_raw if sid.strip().isdigit()]

        if name:
            class_group.name = name
        class_group.students.set(student_ids)
        class_group.save()
        messages.success(request, f"Клас «{name}» оновлено.")

    return redirect("manage_classes")


# ---------- ГРУПИ ВЧИТЕЛІВ ----------

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
