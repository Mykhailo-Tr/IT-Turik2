from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Student, Teacher, Parent, TeacherGroup, ClassGroup


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ("email", "first_name", "last_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "role")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "role", "is_active", "is_staff"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("get_full_name", "school_class")
    search_fields = ("user__first_name", "user__last_name", "school_class")

    @admin.display(description="Ім'я")
    def get_full_name(self, obj):
        return obj.user.get_full_name()


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("get_full_name", "subject")
    search_fields = ("user__first_name", "user__last_name", "subject")

    @admin.display(description="Ім'я")
    def get_full_name(self, obj):
        return obj.user.get_full_name()


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("get_full_name", "get_children")
    search_fields = ("user__first_name", "user__last_name", "children__user__first_name")

    @admin.display(description="Ім'я")
    def get_full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description="Діти")
    def get_children(self, obj):
        return ", ".join(child.user.get_full_name() for child in obj.children.all())


@admin.register(TeacherGroup)
class TeacherGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "get_teachers")
    search_fields = ("name", "teachers__user__first_name", "teachers__user__last_name")

    @admin.display(description="Вчителі")
    def get_teachers(self, obj):
        return ", ".join(teacher.get_full_name() for teacher in obj.teachers.all())
    
@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "get_class_names")
    search_fields = ("name",)

    @admin.display(description="Класи")
    def get_class_names(self, obj):
        return ", ".join(obj.class_names) if obj.class_names else "Немає класів"