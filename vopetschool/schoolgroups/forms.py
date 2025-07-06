from django import forms
from accounts.models import Teacher
from .models import ClassGroup, TeacherGroup


class ClassGroupCreateForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = ['name']
        labels = {'name': 'Назва класу'}

class TeacherGroupCreateForm(forms.ModelForm):
    class Meta:
        model = TeacherGroup
        fields = ['name', 'teachers']
        widgets = {'teachers': forms.CheckboxSelectMultiple}
        labels = {'name': 'Назва групи', 'teachers': 'Виберіть вчителів'}

class TeacherGroupEditForm(forms.ModelForm):
    class Meta:
        model = TeacherGroup
        fields = ['name', 'teachers']
        widgets = {
            'teachers': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teachers'].queryset = Teacher.objects.select_related('user').all()
        self.fields['teachers'].label_from_instance = lambda obj: obj.user.get_full_name()