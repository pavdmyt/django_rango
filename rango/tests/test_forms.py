from django.contrib.auth.models import User
from django.test import TestCase

from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.tests.test_views import add_cat


class CategoryFormTest(TestCase):

    def test_valid_data(self):
        """
        Checks that form is valid and that created models.Category
        object is filled with expected data.
        """
        # Check form.
        form = CategoryForm(data={'name': 'Foo Bar'})
        self.assertTrue(form.is_valid())

        # Check Category.
        category = form.save()
        self.assertEqual(category.name, 'Foo Bar')
        self.assertEqual(category.views, 0)
        self.assertEqual(category.likes, 0)
        self.assertEqual(category.slug, 'foo-bar')

    def test_blank_data(self):
        """
        Checks form with blank data and corresponding form errors.
        """
        form = CategoryForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'name': ['This field is required.']})


class PageFormTest(TestCase):

    def setUp(self):
        self.cat = add_cat('rango_test', 0, 0)

    def test_valid_data(self):
        """
        Checks that form is valid and that created models.Page
        object is filled with expected data.
        """
        # Check form.
        form_data = {'title': 'Test Page',
                     'url':   'http://example.com/'}
        form = PageForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Check Page.
        page = form.save(commit=False)
        page.category = self.cat
        page.save()

        self.assertEqual(page.category, self.cat)
        self.assertEqual(page.title, 'Test Page')
        self.assertEqual(page.url, form_data.get('url'))
        self.assertEqual(page.views, 0)
        self.assertEqual(page.last_visit, None)
        self.assertEqual(page.first_visit, None)

    def test_blank_data(self):
        """
        Checks form with blank data and corresponding form errors.
        """
        form = PageForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'title': ['This field is required.'],
                                       'url':   ['This field is required.']})


class UserFormTest(TestCase):

    def test_valid_data(self):
        """
        Checks that form is valid and that created
        django.contrib.auth.models.User object is filled
        with expected data.
        """
        # Check form.
        form_data = {'username': 'test_user',
                     'password': '1234'}
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Check User.
        user = form.save()
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.password, '1234')
        self.assertEqual(user.email, '')
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')

    def test_blank_data(self):
        """
        Checks form with blank data and corresponding form errors.
        """
        form = UserForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'username': ['This field is required.'],
                          'password': ['This field is required.']})


class UserProfileFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user',
                                             password='1234')

    def test_valid_data(self):
        """
        Checks that form is valid and that created models.UserProfile
        object is filled with expected data.
        """
        # Check form.
        form = UserProfileForm(data={'website': 'http://example.com/'})
        self.assertTrue(form.is_valid())

        # Check UserProfile.
        up = form.save(commit=False)
        up.user = self.user
        up.save()

        self.assertEqual(up.user, self.user)
        self.assertEqual(up.website, 'http://example.com/')
        self.assertEqual(up.picture.name, '')
