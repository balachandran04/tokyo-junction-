from django import forms
from .models import user_register

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = user_register
        fields = ['Name', 'Phone', 'Email', 'Password', 'Address', 'Profile']


    def clean_Phone(self):
        phone = self.cleaned_data.get('Phone')
        if len(str(phone)) != 10:
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phone

    def clean_Password(self):
        password = self.cleaned_data.get('Password')

        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters.")
        return password
