import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase

from rango.models import Category, Page


class IndexViewTests(TestCase):

    #
    # Categories
    #
    def test_index_view_with_no_categories(self):
        """
        If no categories exist, an appropriate msg should be displayed.
        """
        response = self.client.get(reverse('index'))
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
        response = self.client.get(reverse('index'))
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
        response = self.client.get(reverse('index'))
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
        response = self.client.get(reverse('index'))
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
        response = self.client.get(reverse('index'))
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
        response = self.client.get(reverse('index'))
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
        # response = self.client.get(reverse('index'))
        self.client.get(reverse('index'))
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
        self.client.get(reverse('index'))
        session = self.client.session

        self.assertEqual(session.get('visits'), 2)


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
