from django.conf.urls import patterns, url
from items import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^winrate/$', views.ItemWinrateView.as_view(), name='winrate'),
    url(r'^(?P<item_name>[a-zA-Z0-9\-]*)/$', views.detail, name='detail'),
)
