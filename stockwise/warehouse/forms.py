from django import forms
from stock_management.models import Material

class UpdateMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['current_amount']
        widgets = {
            'current_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
