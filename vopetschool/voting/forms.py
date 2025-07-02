# forms.py

from django import forms
from django.forms import formset_factory, BaseFormSet

from .models import Vote, VoteOption
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
            "multiple_choices_allowed", "has_correct_answer", "participants"
        ]
        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "participants": forms.SelectMultiple(attrs={"size": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["participants"].queryset = User.objects.all()
        self.fields["participants"].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("Дата початку повинна бути раніше дати завершення.")

        return cleaned_data
    
    def clean_title(self):
        title = self.cleaned_data.get("title")
        if not title:
            raise forms.ValidationError("Назва голосування не може бути порожньою.")
        return title


class VoteOptionForm(forms.Form):
    text = forms.CharField(label="Варіант", max_length=200)
    is_correct = forms.BooleanField(required=False, label="Правильний (для тестів)")


VoteOptionFormSet = formset_factory(VoteOptionForm, extra=0, min_num=2, validate_min=True, can_delete=True,)