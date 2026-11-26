from django import forms
from django.core.validators import RegexValidator


class CheckoutForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), label="Delivery address")
    phone = forms.CharField(
        max_length=15, label="Phone number",
        validators=[RegexValidator(r"^\+?\d{10,14}$", "Enter a valid phone number (10-14 digits).")],
    )
