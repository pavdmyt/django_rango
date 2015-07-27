from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings  # for media server

from rango import views

from registration.backends.simple.views import RegistrationView


class MyRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return '/rango/add_profile/'


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'django_rango.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')),
    url(r'^accounts/register/$', MyRegistrationView.as_view(),
        name='registration_register'),
    (r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/user/settings/$', views.user_settings, name='user_settings'),
)


# Wire up API.
urlpatterns += patterns(
    '',
    url(r'^api/categories/$',
        views.CategoriesViewSet.as_view(),
        name='cat-list'),

    url(r'^api/pages/$',
        views.PagesViewSet.as_view(),
        name='page-list'),

    url(r'^api/categories/(?P<cat_id>[\d]+)/$',
        views.category_details,
        name='specific-cat'),

    url(r'^api/pages/(?P<page_id>[\d]+)/$',
        views.page_details,
        name='specific-page'),
)


# required for media server

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
         'serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
