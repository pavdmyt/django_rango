from django import forms
from django.contrib.auth.models import User

from rango.models import Page, Category, UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           help_text="Please enter the category name.")
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # provides additional information on the form
    # (defines which model we're wanting to provide a form for)
    class Meta:
        # provide an association between the ModelForm and a model
        model = Category

        # specify fields we wish to include into the form
        fields = ('name',)


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200,
                         help_text="Please enter the URL of the page.")

    class Meta:
        # provide an association between the ModelForm and a model
        model = Page

        # We don't need every field in the model present.
        # Here, we are hiding the foreign key.
        # we can either exclude the category field from the form:
        exclude = ('category', 'first_visit', 'last_visit', 'views')
        # or specify the fields to include:
        # fields = ('title', 'url', 'views')


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
