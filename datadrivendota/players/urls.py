from django.conf.urls import patterns, url
from players import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^winrate/$', views.winrate, name='player_winrate'),
    url(r'^timeline/$', views.timeline, name='timeline'),
    url(
        r'^management/$',
        views.player_management,
        name="management"
    ),
    url(
        r'^(?P<player_id>[0-9]*)/matches/$',
        views.player_matches,
        name="id_matches"
    ),

    url(
        r'^(?P<player_id>[0-9]*)/$',
        views.detail,
        name="id_detail"
    ),

    url(r'^api/getplayers/$', views.player_list, name='player_list'),

)
