from django.contrib import admin
from rango.models import Category, Page


# update Page model view at admin interface

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


# re-order fields in the Category edit form

class CatAdmin(admin.ModelAdmin):
    fields = ['name', 'likes', 'views']


# register my models

admin.site.register(Category, CatAdmin)
admin.site.register(Page, PageAdmin)