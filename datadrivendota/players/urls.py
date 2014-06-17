from django.conf.urls import patterns, url
from players import views

urlpatterns = patterns(
    '',
    url(r'^$', views.pro_index, name='pro_index'),
    url(r'^followed/$', views.followed_index, name='followed_index'),
    url(r'^all-players/$', views.index, name='index'),
    url(
        r'^winrate/$',
        views.Winrate.as_view(),
        name='player_winrate'
    ),
    url(
        r'^hero-adversary/$',
        views.HeroAdversary.as_view(),
        name='hero_adversary'),
    url(
        r'^hero-ability-comparison/$',
        views.HeroAbilities.as_view(),
        name='hero_abilities'
    ),
    url(
        r'^management/$',
        views.player_management,
        name="management"
    ),
    url(
        r'^management/match-request/$',
        views.MatchRequestView.as_view(),
        name="match_request"
    ),
    url(
        r'^management/tracking/$',
        views.TrackingView.as_view(),
        name="tracking"
    ),
    url(
        r'^management/following/$',
        views.FollowView.as_view(),
        name="following"
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
    url(
        r'^hero-style/(?P<player_id>[0-9]*)-(?P<hero_name>[a-zA-Z0-9\-]*)$',
        views.hero_style,
        name='hero_style'
    ),
    url(
        r'^comparison/(?P<player_id_1>[0-9]*)-(?P<player_id_2>[0-9]*)/$',
        views.comparison,
        name="comparison"
    ),
    url(
        r'^data-request/$',
        views.data_applicant,
        name="data_applicant"
    ),

    url(r'^api/getplayers/$', views.player_list, name='player_list'),
    url(r'^api/dropfollow/$', views.drop_follow, name='drop_follow'),
    url(r'^api/checkid/$', views.check_id, name='check_id'),
    url(r'^api/addtrack/$', views.add_track, name='add_track'),
    url(
        r'^api/winrate/$',
        views.ApiWinrateChart.as_view(),
        name='api_winrate_chart'
        ),
    url(
        r'^api/hero-adversary/$',
        views.HeroAdversary.as_view(),
        name='api_hero_adversary_chart'
        ),
    url(
        r'^api/hero-abilities/$',
        views.ApiHeroAbilities.as_view(),
        name='api_hero_abilities_chart'
        ),
    url(
        r'^api/versus-winrate/$',
        views.ApiVersusWinrate.as_view(),
        name='api_versus_winrate_chart'
        ),
    url(
        r'^api/role/$',
        views.ApiRole.as_view(),
        name='api_role_chart'
        ),

)
