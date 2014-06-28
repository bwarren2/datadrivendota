from django.conf.urls import patterns, url
from leagues import views

urlpatterns = patterns(
    '',
    url(r'^$', views.LeagueList.as_view(), name='index'),
    url(
        r'^(?P<steam_id>[0-9\-]*)/$',
        views.LeagueDetail.as_view(),
        name='detail'
    ),
    url(
        r'^winrate/$',
        views.Winrate.as_view(),
        name='team_winrate'
    ),
    url(
        r'^pick-ban/$',
        views.PickBan.as_view(),
        name='pick_ban'
    ),
    url(r'^api/getleagues/$', views.league_list, name='league_list'),
    url(
        r'^api/winrate/$',
        views.ApiWinrateChart.as_view(),
        name='api_winrate_chart'
        ),
    url(
        r'^api/pick-ban/$',
        views.ApiPickBanChart.as_view(),
        name='api_pick_ban_chart'
        ),
)
