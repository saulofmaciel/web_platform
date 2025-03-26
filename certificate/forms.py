# forms.py
from django import forms
from .models import Certificate, Issuer, Customer, Country, UserIssuer, UserCustomer


class CertificateForm(forms.ModelForm):
    # Add a checkbox field to decide whether add watermark
    add_stamp = forms.BooleanField(required=False, label="Add stamp")
    class Meta:
        model = Certificate
        fields = 'description', 'type', 'file', 'language', 'issuer', 'customer'

class IssuerForm(forms.ModelForm):
    class Meta:
        model = Issuer
        fields = '__all__'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = '__all__'

class UserIssuerForm(forms.ModelForm):
    class Meta:
        model = UserIssuer
        fields = '__all__'

class UserCustomerForm(forms.ModelForm):
    class Meta:
        model = UserCustomer
        fields = '__all__'