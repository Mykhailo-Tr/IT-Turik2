from django.shortcuts import render, redirect, get_object_or_404
from .models import ClassGroup, TeacherGroup
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.forms import modelformset_factory
from .forms import ClassGroupCreateForm, TeacherGroupCreateForm, TeacherGroupEditForm

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
        return render(request, "schoolgroups/manage_classes.html", context)

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
        return render(request, "schoolgroups/manage_teacher_groups.html", context)

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
