from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User, Student, Teacher, Parent
from schoolgroups.models import ClassGroup, TeacherGroup


class RoleChoiceForm(forms.Form):
    role = forms.ChoiceField(choices=User.Role.choices, label="Оберіть роль")


class BaseRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Пароль",
        help_text="Мінімум 8 символів. Використовуйте букви, цифри і спеціальні символи."
    )
    password2 = forms.CharField(widget=forms.PasswordInput, label="Підтвердження пароля")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Користувач з таким email вже існує.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            self.add_error('password2', "Паролі не співпадають")

        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)

        return cleaned_data

    def save_user(self, role, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = role
        if commit:
            user.save()
        return user


class StudentRegisterForm(BaseRegisterForm):
    class_group = forms.ModelChoiceField(
        queryset=ClassGroup.objects.all(),
        required=False,
        label="Клас (необов'язково)"
    )

    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields + ['class_group']

    def save(self, commit=True):
        user = self.save_user(User.Role.STUDENT, commit=commit)
        if commit:
            student = Student.objects.create(user=user)
            if self.cleaned_data.get("class_group"):
                self.cleaned_data["class_group"].students.add(student)
        return user


class TeacherRegisterForm(BaseRegisterForm):
    subject = forms.CharField(label="Предмет")
    groups = forms.ModelMultipleChoiceField(
        queryset=TeacherGroup.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Групи викладання"
    )

    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields + ['subject', 'groups']

    def save(self, commit=True):
        user = self.save_user(User.Role.TEACHER, commit=commit)
        if commit:
            teacher = Teacher.objects.create(user=user, subject=self.cleaned_data["subject"])
            teacher.groups.set(self.cleaned_data["groups"])
        return user


class ParentRegisterForm(BaseRegisterForm):
    children = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Діти (опціонально)"
    )

    class Meta(BaseRegisterForm.Meta):
        fields = BaseRegisterForm.Meta.fields + ['children']

    def save(self, commit=True):
        user = self.save_user(User.Role.PARENT, commit=commit)
        if commit:
            parent = Parent.objects.create(user=user)
            parent.children.set(self.cleaned_data["children"])
        return user


class DirectorRegisterForm(BaseRegisterForm):
    def save(self, commit=True):
        return self.save_user(User.Role.DIRECTOR, commit=commit)


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class EditProfileForm(forms.ModelForm):
    subject = forms.CharField(label="Предмет", required=False)
    class_group = forms.ModelChoiceField(
        queryset=ClassGroup.objects.all(),
        required=False,
        label="Клас"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if self.user.role == 'teacher':
            self.fields['subject'].initial = self.user.teacher.subject
        else:
            self.fields.pop('subject')

        if self.user.role == 'student':
            student = self.user.student
            self.fields['class_group'].initial = student.get_class_group()
        else:
            self.fields.pop('class_group')

    def save(self, commit=True):
        user = super().save(commit)
        
        if self.user.role == 'teacher':
            self.user.teacher.subject = self.cleaned_data.get("subject")
            if commit:
                self.user.teacher.save()

        if self.user.role == 'student':
            student = self.user.student
            new_class_group = self.cleaned_data.get("class_group")
            student.class_groups.clear()
            if new_class_group:
                new_class_group.students.add(student)

        return user