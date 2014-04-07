from django.conf.urls import patterns, url
from players import views

urlpatterns = patterns(
    '',
    url(r'^$', views.pro_index, name='pro_index'),
    url(r'^followed/$', views.followed_index, name='followed_index'),
    url(r'^all-players/$', views.index, name='index'),
    url(r'^winrate/$', views.winrate, name='player_winrate'),
    url(r'^timeline/$', views.timeline, name='timeline'),
    url(r'^hero-adversary/$', views.player_hero_side, name='hero_adversary'),
    url(
        r'^hero_ability_comparison/$',
        views.hero_abilities,
        name='hero_abilities'
    ),
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
    url(r'^hero-style/(?P<player_id>[0-9]*)-(?P<hero_name>[a-zA-Z0-9\-]*)$', views.hero_style, name='hero_style'),
    url(
        r'^comparison/(?P<player_id_1>[0-9]*)-(?P<player_id_2>[0-9]*)/$',
        views.comparison,
        name="comparison"
    ),

    url(r'^api/getplayers/$', views.player_list, name='player_list'),
    url(r'^api/dropfollow/$', views.drop_follow, name='drop_follow'),
    url(r'^api/checkid/$', views.check_id, name='check_id'),
    url(r'^api/addtrack/$', views.add_track, name='add_track'),

)
