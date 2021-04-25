from django import forms
from django_registration.forms import RegistrationFormUniqueEmail, RegistrationFormCaseInsensitive
from django.utils.translation import gettext_lazy as _
from .models import User


class RegistrationForm(RegistrationFormCaseInsensitive, RegistrationFormUniqueEmail):
    eth_address = forms.CharField(
        label=_("Ethereum Address"),
        widget=forms.TextInput(attrs={'autocomplete': 'new-password'}),
        strip=True,
        help_text=_("Enter your Ethereum address."),
    )

    class Meta(RegistrationFormCaseInsensitive.Meta):
        model = User
        fields = RegistrationFormCaseInsensitive.Meta.fields + [
            'eth_address',
        ]
