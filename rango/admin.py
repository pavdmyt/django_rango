from django.contrib import admin
from rango.models import Category, Page


# update Page model view at admin interface

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


# register my models

admin.site.register(Category)
admin.site.register(Page, PageAdmin)