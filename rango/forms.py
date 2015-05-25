from django import forms
from rango.models import Page, Category


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # provides additional information on the form
    # (defines which model we're wanting to provide a form for)
    class Meta:
        # provide an association between the ModelForm and a model
        model = Category

        # specify fields we wish to include into the form
        fields = ('name',)


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        # provide an association between the ModelForm and a model
        model = Page

        # We don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them.
        # Here, we are hiding the foreign key.
        # we can either exclude the category field from the form:
        exclude = ('category',)
        # or specify the fields to include (i.e. not include the category field)
        # fields = ('title', 'url', 'views')
