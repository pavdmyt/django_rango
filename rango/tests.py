from django.test import TestCase
from django.core.urlresolvers import reverse

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


class IndexViewTests(TestCase):

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
        add_cat('test', 1, 1)
        add_cat('spam', 1, 1)
        add_cat('eggs', 1, 1)
        add_cat('foo bar', 1, 1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "foo bar")

        cats_num = len(response.context['categories'])
        self.assertEqual(cats_num, 4)


#######################################################################
# Helper functions

def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c
