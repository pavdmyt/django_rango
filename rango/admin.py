from django.contrib import admin
from rango.models import Category, Page, UserProfile


# update Page model view at admin interface

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url', 'views')


# re-order fields in the Category edit form

class CatAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    fields = ['name', 'slug', 'likes', 'views']


# register my models

admin.site.register(Category, CatAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
