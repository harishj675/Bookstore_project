from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        label='username',
        max_length=20,
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
        self.helper.add_input(Submit('submit', 'Submit'))
