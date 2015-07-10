from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        # Ensure views >= 0
        if self.views < 0:
            self.views = 0

        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):  # use __str__ in Python 3
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    # Make these fields optional.
    last_visit = models.DateTimeField('last visit', blank=True, null=True)
    first_visit = models.DateTimeField('first visit', blank=True, null=True)

    def save(self, *args, **kwargs):
        now = timezone.now()

        # Ensure visits are not in the future.
        if self.last_visit:
            if self.last_visit > now:
                self.last_visit = None
                print("***Warning: last_visit > now, field set to 'None'")

        if self.first_visit:
            if self.first_visit > now:
                self.first_visit = None
                print("***Warning: first_visit > now, field set to 'None'")

        # Ensure first_visit < last_visit.
        if self.first_visit and self.last_visit:
            if self.first_visit > self.last_visit:
                self.first_visit = None
                print(
                    "***Warning: first_visit > last_visit, field set to 'None'")

        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):  # use __str__ in Python 3
        return self.title


class UserProfile(models.Model):
    # Link UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # Additional user attributes.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __unicode__(self):
        return self.user.username
