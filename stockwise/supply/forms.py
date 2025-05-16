# supplier/forms.py

from django import forms
from stock_management.models import Offer

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['unit_price', 'quantity_per_price', 'total_quantity']

    def clean(self):
        cleaned_data = super().clean()
        quantity_per_price = cleaned_data.get('quantity_per_price')
        total_quantity = cleaned_data.get('total_quantity')

        if quantity_per_price and total_quantity and quantity_per_price > total_quantity:
            self.add_error('quantity_per_price', 'Quantity per price cannot be greater than total quantity.')
