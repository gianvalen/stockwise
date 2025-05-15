# supplier/forms.py

from django import forms
from stock_management.models import Offer

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['unit_price', 'quantity_per_price', 'total_quantity']
