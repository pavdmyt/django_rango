from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings  # for media server

from rango import views

from registration.backends.simple.views import RegistrationView


class MyRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return '/rango/'


urlpatterns = patterns('',
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


# required for media server

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )
