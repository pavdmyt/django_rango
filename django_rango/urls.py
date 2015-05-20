from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings  # for media server


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_rango.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')),
)


# required for media server

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )
