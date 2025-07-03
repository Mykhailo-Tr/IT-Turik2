# forms.py

from django import forms
from django.forms import formset_factory, BaseFormSet

from .models import Vote, VoteOption
from accounts.models import TeacherGroup, ClassGroup

from accounts.models import User

class VoteForm(forms.Form):
    def __init__(self, vote: Vote, *args, **kwargs):
        super().__init__(*args, **kwargs)

        options = vote.options.all()
        choices = [(option.id, option.text) for option in options]

        if vote.multiple_choices_allowed:
            self.fields["options"] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                label="Оберіть один або кілька варіантів"
            )
        else:
            self.fields["options"] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label="Оберіть один варіант"
            )


class VoteCreateForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = [
            "title", "description", "level", "start_date", "end_date",
            "multiple_choices_allowed", "has_correct_answer",
            "participants", "teacher_groups", "class_groups"
        ]
        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "participants": forms.SelectMultiple(attrs={"size": 10}),
            "teacher_groups": forms.SelectMultiple(attrs={"size": 5}),
            "class_groups": forms.SelectMultiple(attrs={"size": 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Отримаємо автора
        super().__init__(*args, **kwargs)

        qs = User.objects.all()
        if user:
            qs = qs.exclude(id=user.id)  # Прибрати автора зі списку

        self.fields["participants"].queryset = qs
        self.fields["teacher_groups"].queryset = TeacherGroup.objects.all()
        self.fields["class_groups"].queryset = ClassGroup.objects.all()

        self.fields["participants"].required = False
        self.fields["teacher_groups"].required = False
        self.fields["class_groups"].required = False




class VoteOptionForm(forms.Form):
    text = forms.CharField(label="Варіант", max_length=200)
    is_correct = forms.BooleanField(required=False, label="Правильний (для тестів)")


VoteOptionFormSet = formset_factory(VoteOptionForm, extra=0, min_num=2, validate_min=True, can_delete=True,)