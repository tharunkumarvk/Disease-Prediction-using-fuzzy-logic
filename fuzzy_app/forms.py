# fuzzy_app/forms.py
from django import forms
from .models import Symptom

class SymptomInputForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        symptoms = Symptom.objects.all()
        for symptom in symptoms:
            self.fields[f'symptom_{symptom.id}'] = forms.FloatField(
                label=symptom.name,
                min_value=symptom.min_value,
                max_value=symptom.max_value,
                required=False
            )