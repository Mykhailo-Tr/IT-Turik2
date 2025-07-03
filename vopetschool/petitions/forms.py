from django import forms
from .models import Petition

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
