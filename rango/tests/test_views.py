import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from rango.models import Category, Page, UserProfile
from rango.views import get_category_list


class IndexViewTests(TestCase):

    def setUp(self):
        # Name attribute from urlpatterns.
        self.urlpat_name = 'index'

    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template(s).
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)

        base_template = 'base.html'
        page_template = 'rango/index.html'

        self.assertTemplateUsed(response, base_template)
        self.assertTemplateUsed(response, page_template)

    #
    # Categories
    #
    def test_index_view_with_no_categories(self):
        """
        If no categories exist, an appropriate msg should be displayed.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        """
        Checks response if categories exist.
        """
        # Populate DB.
        add_cat('test', 1, 1)
        add_cat('spam', 1, 1)
        add_cat('eggs', 1, 1)
        add_cat('foo bar', 1, 1)

        # Test.
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "foo bar")

        cats_num = len(response.context['categories'])
        self.assertEqual(cats_num, 4)

    def test_top5_cats_sorted_by_likes(self):
        """
        Checks context contains top 5 categories sorted by likes.
        """
        # Populate DB.
        add_cat('test1', 1, 1)
        add_cat('test2', 1, 2)
        add_cat('test3', 1, 3)
        add_cat('test4', 1, 4)
        add_cat('test5', 1, 5)
        add_cat('test6', 1, 6)
        add_cat('test7', 1, 7)

        # Test.
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['categories'],
            ['<Category: test7>',
             '<Category: test6>',
             '<Category: test5>',
             '<Category: test4>',
             '<Category: test3>'])

        cats_num = len(response.context['categories'])
        self.assertEqual(cats_num, 5)

    #
    # Pages
    #
    def test_index_view_with_no_pages(self):
        """
        If no pages exist, an appropriate msg should be displayed.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no pages present.")
        self.assertQuerysetEqual(response.context['pages'], [])

    def test_index_view_with_pages(self):
        """
        Checks response if pages exist.
        """
        # Populate DB.
        cat = add_cat('test', 1, 1)
        url = 'http://example.com'

        add_page(cat=cat, name='spam', url=url)
        add_page(cat=cat, name='eggs', url=url)
        add_page(cat=cat, name='foo', url=url)
        add_page(cat=cat, name='bar', url=url)

        # Test.
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "foo")

        pages_num = len(response.context['pages'])
        self.assertEqual(pages_num, 4)

    def test_top5_pages_sorted_by_views(self):
        """
        Checks context contains top 5 pages sorted by views.
        """
        # Populate DB.
        url = 'http://example.com'
        cat = add_cat('test1', 1, 1)

        add_page(cat=cat, name='test1', url=url, views=1)
        add_page(cat=cat, name='test2', url=url, views=2)
        add_page(cat=cat, name='test3', url=url, views=3)
        add_page(cat=cat, name='test4', url=url, views=4)

        cat = add_cat('test2', 1, 2)

        add_page(cat=cat, name='test5', url=url, views=5)
        add_page(cat=cat, name='test6', url=url, views=6)
        add_page(cat=cat, name='test7', url=url, views=7)

        # Test.
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['pages'],
            ['<Page: test7>',
             '<Page: test6>',
             '<Page: test5>',
             '<Page: test4>',
             '<Page: test3>'])

        cats_num = len(response.context['pages'])
        self.assertEqual(cats_num, 5)

    #
    # Session
    #
    def test_session_data_is_set(self):
        """
        Checks that session data about last visit time and number
        of visits is set up by a view.
        """
        self.client.get(reverse(self.urlpat_name))
        session = self.client.session

        self.assertEqual('last_visit' in session, True)
        self.assertEqual('visits' in session, True)

    def test_visits_calculated_once_per_day(self):
        """
        Checks that visits are counted every 24 hours user
        access Rango index page.
        """
        # Ugly and long creation of session with
        # `last_visit` and `visits` parameters.
        from django.conf import settings
        from importlib import import_module
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        # Mandatory!
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        # Last visit 1 day ago.
        now = datetime.datetime.now()
        time = now - datetime.timedelta(days=1)

        # Set session parameters.
        store.update({'last_visit': str(time), 'visits': 1})
        store.save()
        self.client.session[settings.SESSION_ENGINE] = store

        # Get response.
        self.client.get(reverse(self.urlpat_name))
        session = self.client.session

        self.assertEqual(session.get('visits'), 2)


class AboutViewTests(TestCase):

    def setUp(self):
        # Name attribute from urlpatterns.
        self.urlpat_name = 'about'

    def test_status_code(self):
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)

    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/about.html')


class CategoryViewTests(TestCase):

    def setUp(self):
        self.url = 'http://testserver/rango/category/'
        self.cat = add_cat('rango_test', 1, 1)

    #
    # Main functionality.
    #
    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template(s).
        """
        response = self.client.get(self.url + self.cat.slug + '/')
        self.assertEqual(response.status_code, 200)

        base_template = 'base.html'
        page_template = 'rango/category.html'

        self.assertTemplateUsed(response, base_template)
        self.assertTemplateUsed(response, page_template)

    def test_category_name_context(self):
        """
        Checks `category_name` contains desired data.
        """
        response = self.client.get(self.url + self.cat.slug + '/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category_name'],
                         self.cat.name)

    def test_pages_context_sorted_by_views(self):
        """
        Checks `pages` context contains all pages sorted by views.
        """
        # Populate DB.
        url = 'http://example.com'

        add_page(cat=self.cat, name='test1', url=url, views=1)
        add_page(cat=self.cat, name='test2', url=url, views=2)
        add_page(cat=self.cat, name='test3', url=url, views=3)
        add_page(cat=self.cat, name='test4', url=url, views=4)
        add_page(cat=self.cat, name='test5', url=url, views=5)
        add_page(cat=self.cat, name='test6', url=url, views=6)
        add_page(cat=self.cat, name='test7', url=url, views=7)

        # Test.
        response = self.client.get(self.url + self.cat.slug + '/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['pages'],
            ['<Page: test7>',
             '<Page: test6>',
             '<Page: test5>',
             '<Page: test4>',
             '<Page: test3>',
             '<Page: test2>',
             '<Page: test1>'])

        cats_num = len(response.context['pages'])
        self.assertEqual(cats_num, 7)

    def test_category_context(self):
        """
        Checks `category` contains desired data.
        """
        response = self.client.get(self.url + self.cat.slug + '/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['category'], Category)

    def test_cat_name_slug_context(self):
        """
        Checks `cat_name_slug` contains desired data.
        """
        cat_name_slug = self.cat.slug
        response = self.client.get(self.url + cat_name_slug + '/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cat_name_slug'], cat_name_slug)

    def test_category_view_with_non_exist_category(self):
        """
        If category doesn't exist, an appropriate msg
        should be displayed.
        """
        category_slug = 'no-such-category'
        response = self.client.get(self.url + category_slug + '/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "The specified category does not exist!")

    #
    # Searching
    #
    # !!!TODO: add appropriate tests.


class AddCategoryViewTests(TestCase):

    def setUp(self):
        # Create test user in test DB.
        self.user = User.objects.create_user(username='test_user',
                                             password='1234')
        # Name attribute from urlpatterns.
        self.urlpat_name = 'add_category'

    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template(s).
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)

        base_template = 'base.html'
        page_template = 'rango/add_category.html'

        self.assertTemplateUsed(response, base_template)
        self.assertTemplateUsed(response, page_template)

    def test_if_no_auth_redirect_to_login(self):
        """
        Checks that if user is not logged in he is redirected
        to login page.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('http://testserver/accounts/login/' in response.url)

    def test_page_available_to_auth_user(self):
        """
        Checks that logged in user can access add_category page.
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add new Category")

    def test_user_can_add_category(self):
        """
        Checks that logged in user can add category.
        """
        # Login.
        self.client.login(username='test_user', password='1234')

        # Form data.
        cat_name = 'test category'
        form_data = {'name': cat_name,
                     'views': '1',
                     'likes': '0'}

        # Submit form.
        response = self.client.post(path=reverse(self.urlpat_name),
                                    data=form_data)
        self.assertEqual(response.status_code, 200)

        # Added category is in DB.
        cat = Category.objects.filter(name=cat_name)
        self.assertTrue(cat)
        self.assertTrue(len(Category.objects.all()) == 1)

    def test_form_in_context_no_auth(self):
        """
        Checks `form` context if user is not logged in.
        """
        # Form data.
        form_data = {'name': 'test category',
                     'views': '1',
                     'likes': '0'}

        # Submit form.
        response = self.client.post(path=reverse(self.urlpat_name),
                                    data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertEqual(form.data, {})

    def test_form_not_in_context_auth(self):
        """
        Checks `form` context is not available if user is logged in.
        (Should show Index page instead.)
        """
        # Login.
        self.client.login(username='test_user', password='1234')

        # Form data.
        form_data = {'name': 'test_category',
                     'views': '1',
                     'likes': '0'}

        # Submit form.
        response = self.client.post(path=reverse(self.urlpat_name),
                                    data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(u'form' not in response.context.keys())


class AddPageViewTests(TestCase):

    def setUp(self):
        # Create test user in test DB.
        self.user = User.objects.create_user(username='test_user',
                                             password='1234')

        # Set up category and appropriate URL.
        self.cat = add_cat('rango_test', 1, 1)
        self.url = 'http://testserver/rango/category/'
        self.tail = self.cat.slug + '/add_page/'

    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template(s).
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(self.url + self.tail)
        self.assertEqual(response.status_code, 200)

        base_template = 'base.html'
        page_template = 'rango/add_page.html'

        self.assertTemplateUsed(response, base_template)
        self.assertTemplateUsed(response, page_template)

    def test_if_no_auth_redirect_to_login(self):
        """
        Checks that if user is not logged in he is redirected
        to login page.
        """
        response = self.client.get(self.url + self.tail)
        self.assertEqual(response.status_code, 302)
        self.assertTrue('http://testserver/accounts/login/' in response.url)

    def test_page_available_to_auth_user(self):
        """
        Checks that logged in user can access add_page page.
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(self.url + self.tail)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add a Page to")

    def test_add_page_with_non_exist_category_auth_user(self):
        """
        If category doesn't exist, an appropriate msg
        should be displayed (user is logged in).
        """
        self.client.login(username='test_user', password='1234')
        category_slug = 'no-such-category'
        response = self.client.get(self.url + category_slug + '/add_page/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "The specified category does not exist!")

    def test_add_page_with_non_exist_category_non_auth_user(self):
        """
        If category doesn't exist, not logged in user trying to add
        a new page should be redirected to login page.
        """
        category_slug = 'no-such-category'
        response = self.client.get(self.url + category_slug + '/add_page/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('http://testserver/accounts/login/' in response.url)

    def test_user_can_add_page_to_category(self):
        """
        Checks that logged in user can add page to category.
        """
        # Login.
        self.client.login(username='test_user', password='1234')

        # Form data.
        page_name = 'test page'
        form_data = {'category': self.cat,
                     'title': page_name,
                     'views': '1',
                     'url': 'http://www.example.com'}

        # Submit form.
        response = self.client.post(path=self.url + self.tail,
                                    data=form_data)
        self.assertEqual(response.status_code, 200)

        # Added page is in DB.
        page = Page.objects.filter(title=page_name)
        self.assertTrue(page)
        self.assertTrue(len(Page.objects.all()) == 1)

    def test_first_visit_is_set_up(self):
        """
        Checks that first_visit is set up in time of page addition.
        """
        # Login.
        self.client.login(username='test_user', password='1234')

        # Form data.
        page_name = 'test page'
        form_data = {'category': self.cat,
                     'title': page_name,
                     'views': '1',
                     'url': 'http://www.example.com'}

        # Submit form.
        response = self.client.post(path=self.url + self.tail,
                                    data=form_data)
        now = timezone.now()
        self.assertEqual(response.status_code, 200)

        # Check page first visit.
        page = Page.objects.filter(title=page_name)[0]
        time_delta = now - page.first_visit
        self.assertTrue(time_delta.total_seconds() < 1)

    def test_context_auth_user_get_request(self):
        """
        Checks context if user is logged in (GET request).
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(self.url + self.tail)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertEqual(form.data, {})

        category = response.context['category']
        self.assertEqual(category, self.cat)

        cat_slug = response.context['cat_name_slug']
        self.assertEqual(cat_slug, self.cat.slug)


class UserSettingsViewTests(TestCase):

    def setUp(self):
        # Create test user in test DB.
        self.user = User.objects.create_user(username='test_user',
                                             password='1234')
        # Name attribute from urlpatterns.
        self.urlpat_name = 'user_settings'

    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template(s).
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)

        base_template = 'base.html'
        page_template = 'registration/user_settings.html'

        self.assertTemplateUsed(response, base_template)
        self.assertTemplateUsed(response, page_template)

    def test_if_no_auth_redirect_to_login(self):
        """
        Checks that if user is not logged in he is redirected
        to login page.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('http://testserver/accounts/login/' in response.url)

    def test_page_available_to_auth_user(self):
        """
        Checks that logged in user can access user_settings page.
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Change password")

    def test_context_auth_user(self):
        """
        Checks context if user is logged in.
        """
        # Add user profile.
        userprofile = add_userprofile(user=self.user,
                                      website='http://example.com')

        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)

        profile = response.context['profile']
        self.assertEqual(profile, userprofile)

    def test_user_does_not_have_userprofile(self):
        """
        Checks context if user does not have filled userprofile.
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('profile' not in response.context.keys())


class TrackUrlViewTests(TestCase):

    def setUp(self):
        self.cat = add_cat('rango_test', 1, 1)
        self.page = add_page(cat=self.cat,
                             name='test page',
                             url='http://testserver/rango/about/')
        # Name attribute from urlpatterns.
        self.urlpat_name = 'goto'

    def test_redirect_if_no_page_id_param(self):
        """
        If no page_id parameter in GET request,
        redirect to index page.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/rango/')

    def test_redirect_if_unproper_page_id_param(self):
        """
        If page_id points to non-existent page in DB,
        redirect to index page.
        """
        response = self.client.get(path=reverse(self.urlpat_name),
                                   data={'page_id': 42})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/rango/')

    def test_redirect_to_page_url_if_page_id_param(self):
        """
        If proper page_id parameter in GET request, redirect to
        appropriate page.
        """
        response = self.client.get(path=reverse(self.urlpat_name),
                                   data={'page_id': self.page.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.page.url)

    def test_page_views_increment(self):
        """
        Checks that page.views parameter is incremented every time
        page accessed.
        """
        views = 0
        response = self.client.get(path=reverse(self.urlpat_name),
                                   data={'page_id': self.page.id})
        self.assertEqual(response.status_code, 302)

        page = Page.objects.get(id=self.page.id)
        self.assertEqual(page.views, views + 1)


class LikeCategoryViewTests(TestCase):

    def setUp(self):
        self.cat = add_cat('rango_test', 0, 0)
        self.user = User.objects.create_user(username='test_user',
                                             password='1234')

    def test_cat_likes_increment(self):
        """
        Checks that category.likes parameter is incremented every
        time appropriate request received.
        """
        likes = 0
        self.client.login(username='test_user', password='1234')
        response = self.client.get(path=reverse('like_category'),
                                   data={'category_id': self.cat.id})
        self.assertEqual(response.status_code, 200)

        cat = Category.objects.get(id=self.cat.id)
        self.assertEqual(cat.likes, likes + 1)


class RegisterProfileViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user',
                                             password='1234')
        # Name attribute from urlpatterns.
        self.urlpat_name = 'reg_profile'

    def test_if_no_auth_redirect_to_login(self):
        """
        Checks that if user is not logged in he is redirected
        to login page.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('http://testserver/accounts/login/' in response.url)

    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template(s).
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)

        base_template = 'base.html'
        page_template = 'rango/profile_registration.html'

        self.assertTemplateUsed(response, base_template)
        self.assertTemplateUsed(response, page_template)

    def test_context_auth_user_get_request(self):
        """
        Checks context if user is logged in (GET request).
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertEqual(form.data, {})

    def test_user_can_add_page_to_category(self):
        """
        Checks that logged in user can add page to category.
        """
        # Login.
        self.client.login(username='test_user', password='1234')

        # Form data.
        site = 'http://www.example.com/'
        form_data = {'website': site}

        # Submit form.
        response = self.client.post(path=reverse(self.urlpat_name),
                                    data=form_data)
        self.assertEqual(response.status_code, 302)

        # User profile for test_user is added into DB
        # with additional info.
        up = UserProfile.objects.get(user=self.user)
        self.assertEqual(up.user.username, self.user.username)
        self.assertEqual(up.website, site)
        self.assertTrue(len(UserProfile.objects.all()) == 1)


class SuggestCategoryViewTests(TestCase):

    def setUp(self):
        # Fill test DB with some categories.
        add_cat('Alpha', 1, 1)
        add_cat('Alphabet', 1, 1)
        add_cat('AI', 1, 1)
        add_cat('Aliens', 1, 1)
        add_cat('Spam', 1, 1)
        add_cat('Eggs', 1, 1)
        add_cat('FooBar', 1, 1)
        # Name attribute from urlpatterns.
        self.urlpat_name = 'suggest_category'

    def test_get_category_list(self):
        """
        Ensures that `get_category_list` helper function
        works properly.
        """
        # 1
        cat_lst = get_category_list(0, 'Al')
        self.assertQuerysetEqual(
            cat_lst.order_by('name'),  # order queryset
            ['<Category: Aliens>',
             '<Category: Alpha>',
             '<Category: Alphabet>'])

        # 2
        cat_lst = get_category_list(0, 'S')
        self.assertQuerysetEqual(
            cat_lst.order_by('name'),  # order queryset
            ['<Category: Spam>'])

        # 3
        cat_lst = get_category_list(2, 'A')
        self.assertQuerysetEqual(
            cat_lst, ['<Category: Alpha>', '<Category: Alphabet>'])

        # 4
        cat_lst = get_category_list(2)
        self.assertEqual(cat_lst, [])

    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/cats.html')

    def test_context_with_suggesion_param(self):
        """
        Checks context when 'suggesion' parameter is given
        in GET request.
        """
        response = self.client.get(path=reverse(self.urlpat_name),
                                   data={'suggestion': 'Al'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['cats']), 3)

    def test_context_without_suggesion_param(self):
        """
        Checks context when 'suggesion' parameter is not given
        in GET request.
        """
        response = self.client.get(path=reverse(self.urlpat_name),
                                   data={'suggestion': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cats'], [])


class AutoAddPageViewTests(TestCase):

    def setUp(self):
        self.cat = add_cat('rango_test', 0, 0)
        self.user = User.objects.create_user(username='test_user',
                                             password='1234')
        # Name attribute from urlpatterns.
        self.urlpat_name = 'auto_add_page'

    def test_if_no_auth_redirect_to_login(self):
        """
        Checks that if user is not logged in he is redirected
        to login page.
        """
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('http://testserver/accounts/login/' in response.url)

    def test_request_with_no_params_auth_user(self):
        """
        Checks that proper message is shown if request contains
        no parameters. Also ckecks context.
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No pages currently in category.")

        # Check context.
        self.assertFalse('pages' in response.context)

    def test_proper_template_is_used(self):
        """
        Checks that page is rendered with proper template.
        """
        self.client.login(username='test_user', password='1234')
        response = self.client.get(reverse(self.urlpat_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/page_list.html')

    def test_user_can_add_page(self):
        """
        Checks that logged in user can add page by pressing dedicated
        button which generates AJAX request. Also ckecks context.
        """
        # Login.
        self.client.login(username='test_user', password='1234')

        # AJAX reqest params.
        page_title = 'Python.org'
        params = {'title_data': page_title,
                  'url_data':   'https://www.python.org/',
                  'catid_data': self.cat.id}

        # Submit form.
        response = self.client.get(path=reverse(self.urlpat_name),
                                   data=params)
        self.assertEqual(response.status_code, 200)

        # Added page is in DB.
        page = Page.objects.get(title=page_title)
        self.assertEqual(page.title, page_title)
        self.assertTrue(len(Page.objects.all()) == 1)

        # Check context.
        self.assertQuerysetEqual(response.context['pages'],
                                 ['<Page: Python.org>'])


#######################################################################
# Helper functions

def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


def add_page(cat, name, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=name)[0]
    p.url = url
    p.views = views
    p.save()
    return p


def add_userprofile(user, website):
    up = UserProfile.objects.get_or_create(user=user)[0]
    up.website = website
    up.save()
    return up
