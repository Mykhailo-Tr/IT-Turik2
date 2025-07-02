from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Student, Teacher, Parent

class RoleChoiceForm(forms.Form):
    role = forms.ChoiceField(choices=User.Role.choices, label="Оберіть роль")


class StudentRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    school_class = forms.CharField(label="Клас")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.STUDENT
        if commit:
            user.save()
            Student.objects.create(user=user, school_class=self.cleaned_data['school_class'])
        return user


class TeacherRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    subject = forms.CharField(label="Предмет")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.TEACHER
        if commit:
            user.save()
            Teacher.objects.create(user=user, subject=self.cleaned_data['subject'])
        return user


class ParentRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    children = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Оберіть своїх дітей"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.PARENT
        if commit:
            user.save()
            parent = Parent.objects.create(user=user)
            parent.children.set(self.cleaned_data['children'])
        return user
class DirectorRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.DIRECTOR
        if commit:
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
