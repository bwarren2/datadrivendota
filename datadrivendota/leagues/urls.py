from django.conf.urls import patterns, url
from leagues import views

urlpatterns = patterns(
    '',
    url(r'^$', views.LeagueList.as_view(), name='index'),
    url(
        r'^scheduled-matches/$',
        views.ScheduledMatchList.as_view(),
        name='scheduled_matches'
    ),
    url(
        r'^(?P<steam_id>[0-9\-]*)/$',
        views.LeagueDetail.as_view(),
        name='detail'
    ),
    url(
        r'^live-games/$',
        views.LiveGameListView.as_view(),
        name='live_games'
    ),
    url(
        r'^live-game-detail/(?P<match_id>[0-9\-]*)/$',
        views.LiveGameDetailView.as_view(),
        name='live_game_detail'
    ),
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
    url(
        r'^api/live-league-games/$',
        views.ApiLiveGamesList.as_view(),
        name='api_live_games_list'
    ),
    url(
        r'^api/live-game-detail/(?P<match_id>[0-9\-]*)/$',
        views.ApiLiveGameDetail.as_view(),
        name='api_live_game_detail'
    ),
    url(
        r'^api/live-game-slice/(?P<match_id>[0-9\-]*)/$',
        views.ApiLiveGameSlice.as_view(),
        name='api_live_game_slice'
    ),

)
