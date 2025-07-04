from django import forms
from .models import Petition, Comment
from accounts.models import ClassGroup


class PetitionForm(forms.ModelForm):
    class_group = forms.ModelChoiceField(
        queryset=ClassGroup.objects.all(),
        required=False,
        label="Клас",
        widget=forms.Select(attrs={"class": "form-select rounded-4 shadow-sm"})
    )

    class Meta:
        model = Petition
        fields = ["title", "text", "deadline", "level", "class_group"]
        widgets = {
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control rounded-4 shadow-sm"}),
            "text": forms.Textarea(attrs={
                "rows": 5,
                "class": "form-control rounded-4 shadow-sm"
            }),
            "level": forms.Select(attrs={"class": "form-select rounded-4 shadow-sm"}),
            "title": forms.TextInput(attrs={"class": "form-control form-control-lg rounded-pill shadow-sm"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.role != "student":
            self.fields.clear()
        else:
            self.fields["class_group"].queryset = ClassGroup.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        level = cleaned_data.get("level")
        class_group = cleaned_data.get("class_group")

        if self.user and self.user.role != "student":
            raise forms.ValidationError("Тільки учні можуть створювати петиції.")

        if not cleaned_data.get("title"):
            raise forms.ValidationError("Заголовок обов'язковий.")

        if not cleaned_data.get("text"):
            raise forms.ValidationError("Текст петиції обов'язковий.")

        if level == Petition.Level.CLASS and not class_group:
            raise forms.ValidationError("Оберіть клас для петиції рівня 'Конкретний клас'.")

        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишіть свій коментар...',
                'rows': 3,
            }),
        }
