from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Registration form: email, confirm email, password, confirm password.
    password1/password2 matching and strength checks are inherited from
    Django's UserCreationForm - only the email-confirmation is custom.
    """
    email2 = forms.EmailField(label='Confirm email')

    class Meta:
        model = User
        fields = ('email',)

    field_order = ['email', 'email2', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data.get('email', ''))
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        email2 = cleaned_data.get('email2')
        if email and email2 and email.lower() != email2.lower():
            self.add_error('email2', "Email addresses don't match.")
        return cleaned_data


class EmailAuthenticationForm(AuthenticationForm):
    """Django's login form, relabelled to ask for email instead of username -
    matches our custom User model, which has no username field at all.
    """
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')
