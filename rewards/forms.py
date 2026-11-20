from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
class RedeemForm(forms.Form):
    code = forms.CharField(max_length=20, min_length=8, label="Product code")
    def clean_code(self):
        return self.cleaned_data["code"].replace("-", "").replace(" ", "").upper()
