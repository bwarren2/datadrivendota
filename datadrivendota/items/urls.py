from django.conf.urls.defaults import patterns, url
from items import views

urlpatterns=patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<item_name>[a-zA-Z0-9\-]*)/?$', views.detail, name='detail'),
)
