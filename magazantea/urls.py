from django.conf.urls import include, url
from django.views.decorators.cache import cache_page

import settings# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Chiamate per urlpatterns
from django.views.static import serve
from django.contrib.auth.views import login
from django.contrib.admindocs import urls
import magazzino.views
import magazzino.memcached_status
import magazzino.statistical_views

urlpatterns = [
    url(r'^$', magazzino.views.hello),
    url(r'^admin/doc/', include(urls)),
    url(r'^magazzino/', include(admin.site.urls)),
    url(r'^listarticoli/$', magazzino.views.listbarcode, name='listbarcode'),
#    url(r'^listarticoli/$', cache_page(60 * 15)('magazzino.views.listbarcode')),
    url(r'^listarticoli/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^articolidaordinare/$', magazzino.views.articolidaordinare, name='articolidaordinare'),
    url(r'^memcached_status/$', magazzino.memcached_status.view, name='view'),
    url(r'^accounts/login/$', login),
    url(r'^costiperpaziente/$', magazzino.statistical_views.costi_per_paziente, name='costiperpaziente'),
        ]
