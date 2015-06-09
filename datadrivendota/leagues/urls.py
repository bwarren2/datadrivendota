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

)
