from django import forms
from .models import Petition, Comment   

class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ["title", "text", "deadline", "level"]
        widgets = {
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "text": forms.Textarea(attrs={
                "rows": 5,
                "class": "form-control rounded-4 shadow-sm"
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and self.user.role != "student":
            self.fields.clear()
            
    def clean(self):
        cleaned_data = super().clean()
        if self.user and self.user.role != "student":
            raise forms.ValidationError("Тільки учні можуть створювати петиції.")
        
        if not cleaned_data.get("title"):
            raise forms.ValidationError("Заголовок обов'язковий.")
        
        if not cleaned_data.get("text"):
            raise forms.ValidationError("Текст петиції обов'язковий.")
        
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