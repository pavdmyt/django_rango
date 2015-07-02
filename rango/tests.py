from django.test import TestCase

from rango.models import Category


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
