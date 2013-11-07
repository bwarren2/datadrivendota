from django.conf.urls import patterns, url
from players import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^winrate/$', views.winrate, name='player_winrate'),
    url(r'^timeline/$', views.timeline, name='timeline'),
    url(
        r'^(?:p:(?P<player_name>.*))/matches/$',
        views.player_matches,
        name="name_matches"
    ),
    url(
        r'^(?:pid:(?P<player_id>[0-9]*))/matches/$',
        views.player_matches,
        name="id_matches"
    ),
    url(
        r'^(?:p:(?P<player_name>.*))/$',
        views.detail,
        name="name_detail"
    ),
    url(
        r'^(?:pid:(?P<player_id>[0-9]*))/$',
        views.detail,
        name="id_detail"
    ),

    url(r'^api/getplayers/$', views.player_list, name='player_list'),

)
