from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class BookAddForm(forms.Form):
    title = forms.CharField(
        label='Book Title',
        max_length=200,
        required=True
    )
    author = forms.CharField(
        label='Book Author',
        max_length=200,
        required=True
    )
    price = forms.IntegerField(
        label='Book Price',
        required=True
    )
    discount = forms.IntegerField(
        label='Discount',
        required=False
    )
    quantity = forms.IntegerField(
        label='Book Quantity',
        required=True
    )
    genre = forms.CharField(
        label='Book Genre',
        required=False
    )
    cover_img = forms.ImageField(
        label='Book Cover Image',
    )

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '/book/add/'
        self.helper.add_input(Submit('submit', 'addbook'))

        for field_name, value in initial.items():
            if field_name in self.fields:
                self.fields[field_name].initial = value


class BookAddMoreInfo(forms.Form):
    book_description = forms.CharField(
        label='Book Description',
        widget=forms.Textarea,
        required=True
    )
    book_ISBN_13 = forms.IntegerField(
        label='Book ISBN 13',
        required=False
    )
    book_language = forms.CharField(
        label='Language',
        max_length=100,
        required=False
    )
    book_binding = forms.CharField(
        label='Binding',
        max_length=100,
        required=False
    )
    book_publisher = forms.CharField(
        label='Book Publisher',
        max_length=300,
        required=False
    )
    book_publishing_date = forms.DateField(
        label='Publishing Date',
        required=False
    )
    book_total_pages = forms.IntegerField(
        label='Total Pages',
        required=False
    )
    book_tag = forms.CharField(
        label='Book Tag',
        required=False
    )

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'f/book/{book_id}/add_more_info/'
        self.helper.add_input(Submit('submit', 'Update'))

        for field_name, value in initial.items():
            if field_name in self.fields:
                self.fields[field_name].initial = value


class ExampleForm(forms.Form):
    like_website = forms.TypedChoiceField(
        label="Do you like this website?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial='1',
        required=True,
    )

    favorite_food = forms.CharField(
        label="What is your favorite food?",
        max_length=80,
        required=True,
    )

    favorite_color = forms.CharField(
        label="What is your favorite color?",
        max_length=80,
        required=True,
    )

    favorite_number = forms.IntegerField(
        label="Favorite number",
        required=False,
    )

    notes = forms.CharField(
        label="Additional notes or feedback",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'first arg is the legend of the fieldset',
                'like_website',
                'favorite_number',
                'favorite_color',
                'favorite_food',
                HTML("""
                    <p>We use notes to get better, <strong>please help us {{ username }}</strong></p>
                """),
                'notes'
            ),
            Submit('submit', 'Submit', css_class='button white')
        )
        # self.helper.form_id = 'id-exampleForm'
        # self.helper.form_class = 'blueForms'
        # self.helper.form_method = 'post'
        # self.helper.form_action = 'submit_survey'
        #
        # self.helper.add_input(Submit('submit', 'Submit'))
