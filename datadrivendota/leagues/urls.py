from django.conf.urls import url
from leagues import views

urlpatterns = [
    url(r'^$', views.LeagueOverview.as_view(), name='overview'),
    url(
        r'^(?P<tier>pro|am|premium)/$',
        views.LeagueList.as_view(),
        name='index'
    ),
    url(
        r'^scheduled-matches/$',
        views.ScheduledMatchList.as_view(),
        name='scheduled_matches'
    ),
    url(
        r'^live-matches/$',
        views.LiveMatchList.as_view(),
        name='live_matches'
    ),
    url(
        r'^(?P<steam_id>[0-9\-]*)/$',
        views.LeagueDetail.as_view(),
        name='detail'
    ),
    url(
        r'^(?P<steam_id>[0-9\-]*)/time-walk$',
        views.LeagueDetailTimeWalk.as_view(),
        name='detail-timewalk'
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
]
