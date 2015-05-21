from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):  # use __str__ in Python 3
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):  # use __str__ in Python 3
        return self.title
