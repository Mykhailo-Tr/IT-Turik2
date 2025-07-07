from django import forms
from django.forms import formset_factory

from .models import Vote, VoteOption
from schoolgroups.models import TeacherGroup, ClassGroup
from accounts.models import User


class VoteForm(forms.Form):
    def __init__(self, vote: Vote, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [(option.id, option.text) for option in vote.options.all()]
        field_class = forms.MultipleChoiceField if vote.multiple_choices_allowed else forms.ChoiceField
        widget = forms.CheckboxSelectMultiple if vote.multiple_choices_allowed else forms.RadioSelect

        self.fields["options"] = field_class(
            choices=choices,
            widget=widget,
            label="Оберіть варіант(и)"
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
            "participants": forms.CheckboxSelectMultiple(),
            "teacher_groups": forms.CheckboxSelectMultiple(),
            "class_groups": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["participants"].queryset = User.objects.exclude(id=user.id) if user else User.objects.all()
        self.fields["teacher_groups"].queryset = TeacherGroup.objects.all()
        self.fields["class_groups"].queryset = ClassGroup.objects.all()

        for field in ("participants", "teacher_groups", "class_groups"):
            self.fields[field].required = False


class VoteOptionForm(forms.Form):
    text = forms.CharField(label="Варіант", max_length=200)
    is_correct = forms.BooleanField(required=False, label="Правильний")


VoteOptionFormSet = formset_factory(
    VoteOptionForm,
    extra=0,
    min_num=2,
    validate_min=True,
    can_delete=True,
)
