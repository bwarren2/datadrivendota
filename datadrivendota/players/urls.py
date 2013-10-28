from django.conf.urls import patterns, url
from players import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(
        r'^(pid:(?P<player_id>[0-9]*))|(p:(?P<player_name>.*))/$',
        views.detail,
        name="detail"
    ),
    url(r'^winrate/$', views.winrate, name='player_winrate'),
    url(r'^timeline/$', views.timeline, name='timeline'),
    url(r'^api/getplayers/$', views.player_list, name='player_list')
)
