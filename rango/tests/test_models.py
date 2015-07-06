from datetime import datetime

from django.test import TestCase

from rango.models import Category, Page


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

    def test_visits_are_not_in_the_future(self):
        """
        Checks that the first visit or last visit
        are not in the future.
        """
        pages = Page.objects.all()
        now = datetime.now()

        for page in pages:

            # Check `first_visit`.
            if page.first_visit:
                self.assertEqual((page.first_visit < now), True)

            # Check `last_visit`.
            if page.last_visit:
                self.assertEqual((page.last_visit < now), True)

    def test_last_visit_is_after_first(self):
        """
        Checks that the last visit equal to or after
        the first visit.
        """
        pages = Page.objects.exclude(last_visit=None)

        for page in pages:
            if page.first_visit:
                self.assertEqual((page.first_visit <= page.last_visit), True)
