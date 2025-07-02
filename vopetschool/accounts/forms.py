from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Student, Teacher, Parent


class RoleChoiceForm(forms.Form):
    role = forms.ChoiceField(choices=User.Role.choices, label="Оберіть роль")


class BaseRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Пароль"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Підтвердження пароля"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password and password2 and password != password2:
            self.add_error('password2', "Паролі не співпадають")
        return cleaned_data

    def save_user(self, role, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = role
        if commit:
            user.save()
        return user


class StudentRegisterForm(BaseRegisterForm):
    school_class = forms.CharField(label="Клас")

    def save(self, commit=True):
        user = self.save_user(User.Role.STUDENT, commit=commit)
        if commit:
            Student.objects.create(user=user, school_class=self.cleaned_data["school_class"])
        return user


class TeacherRegisterForm(BaseRegisterForm):
    subject = forms.CharField(label="Предмет")

    def save(self, commit=True):
        user = self.save_user(User.Role.TEACHER, commit=commit)
        if commit:
            Teacher.objects.create(user=user, subject=self.cleaned_data["subject"])
        return user


class ParentRegisterForm(BaseRegisterForm):
    children = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Оберіть своїх дітей"
    )

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
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        labels = {
            'email': 'Email',
            'first_name': "Ім'я",
            'last_name': "Прізвище"
        }

