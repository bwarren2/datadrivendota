from django.conf.urls import patterns, url
from players import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ProIndexView.as_view(), name='pro_index'),
    url(
        r'^(?P<player_id>[0-9]*)/$',
        views.PlayerDetailView.as_view(),
        name="id_detail"
    ),
    url(
        r'^followed/$',
        views.FollowedPlayerIndexView.as_view(),
        name='followed_index'
    ),
    url(r'^all-players/$', views.PlayerIndexView.as_view(), name='index'),
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
        r'^hero-style/(?P<player_id>[0-9]*)-(?P<hero_name>[a-zA-Z0-9\-]*)$',
        views.HeroStyleView.as_view(),
        name='hero_style'
    ),
    url(
        r'^comparison/(?P<player_id_1>[0-9]*)-(?P<player_id_2>[0-9]*)/$',
        views.PlayerComparsionView.as_view(),
        name="comparison"
    ),
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
