from django import forms
from stock_management.models import RequestDetail, Material

class RequestMaterialForm(forms.ModelForm):
    material = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        empty_label="Select a material",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'})
    )

    class Meta:
        model = RequestDetail
        fields = ['material', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can filter or customize queryset here if needed
        # self.fields['material'].queryset = Material.objects.all()
