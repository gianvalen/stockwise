from django import forms
from stock_management.models import InventoryMaterial

class UpdateMaterialForm(forms.ModelForm):
    class Meta:
        model = InventoryMaterial
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
