from django import forms
from stock_management.models import Project

class MaterialTransferForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label="Quantity to Transfer")
    destination_project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        label="Destination Project",
        empty_label="Select a project"
    )
