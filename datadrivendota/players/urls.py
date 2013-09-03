from django.conf.urls.defaults import patterns, url
from players import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(pid:(?P<player_id>[0-9]*))|(p:(?P<player_name>.*))/?$', views.detail, name="detail"),
)
    # Examples:
    # url(r'^$', 'datadrivendota.views.home', name='home'),
    # url(r'^datadrivendota/', include('datadrivendota.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
