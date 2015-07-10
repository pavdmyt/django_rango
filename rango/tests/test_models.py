import datetime
from random import randrange

from django.test import TestCase
from django.utils import timezone

from rango.models import Category, Page
from rango.tests.test_views import add_cat, add_page


class CategoryMethodTests(TestCase):

    def test_ensure_views_are_positive(self):
        """
        Should result True for categories where views are zero
        or positive.
        """
        cat = Category(name='test', views=-1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        """
        Checks to make sure that when category is added, appropriate
        slug line is created i.e.
        "Random Category String" -> "random-category-string"
        """
        cat = Category(name='Random Category String')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string')


class PageMethodTests(TestCase):

    def setUp(self):
        # Populate DB.
        url = 'http://www.example.com/'
        self.cat = add_cat('test cat', 1, 1)
        add_page(self.cat, 'test page1', url)
        add_page(self.cat, 'test page2', url)
        add_page(self.cat, 'test page3', url)
        add_page(self.cat, 'test page4', url)
        add_page(self.cat, 'test page5', url)
        add_page(self.cat, 'test page6', url)
        add_page(self.cat, 'test page7', url)
        add_page(self.cat, 'test page8', url)
        add_page(self.cat, 'test page9', url)
        add_page(self.cat, 'test page10', url)

        # Put first and last visit data to pages.
        self.pages = Page.objects.all()

        for page in self.pages:
            add_random_time(page)

    def test_visits_are_not_in_the_future(self):
        """
        Checks that the first visit or last visit
        are not in the future.
        """
        now = timezone.now()

        # Test.
        for page in self.pages:

            # Check `first_visit`.
            if page.first_visit:
                self.assertEqual((page.first_visit <= now), True)

            # Check `last_visit`.
            if page.last_visit:
                self.assertEqual((page.last_visit <= now), True)

    def test_last_visit_is_after_first(self):
        """
        Checks that the last visit equal to or after
        the first visit.
        """
        for page in self.pages:
            if page.first_visit and page.last_visit:
                self.assertTrue(page.first_visit <= page.last_visit)


#######################################################################
# Helper functions

def add_random_time(page):
    """
    Modifies `page.last_visit` and `page.first_visit` fields
    with random dates (both past or future).
    """
    now = timezone.now()
    page.first_visit = now + datetime.timedelta(days=randrange(-10, 11, 1))
    page.last_visit = now + datetime.timedelta(days=randrange(-10, 11, 1))
    page.save()
