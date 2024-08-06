from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username or Email',
        max_length=100,
        required=True,
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '/users/login/'
        self.helper.add_input(Submit('submit', 'Login'))


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True,
                                 widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Email'}))
    username = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Username'}))
    password1 = forms.CharField(required=True,
                                widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'}))
    password2 = forms.CharField(required=True,
                                widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.Form):
    first_name = forms.CharField(
        label='First Name',
        max_length=100,
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=100
    )
    email = forms.CharField(
        label='Email'
    )
    address = forms.CharField(
        label='Address',
        max_length=100,
    )
    mobile_number = forms.CharField(
        label='Mobile Number',
        max_length=10
    )
    pincode = forms.IntegerField(
        label='Pincode'
    )
