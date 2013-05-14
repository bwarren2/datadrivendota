from django.conf.urls.defaults import patterns, url
from heroes import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^vitals/?$', views.vitals, name='vitals'),
    url(r'^(?P<hero_name>[a-zA-Z0-9\-]*)/?$', views.detail, name="detail"),
)
    # Examples:
    # url(r'^$', 'datadrivendota.views.home', name='home'),
    # url(r'^datadrivendota/', include('datadrivendota.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
