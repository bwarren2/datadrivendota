from django.conf.urls import url, patterns
from matches import views

urlpatterns = patterns(
    '',
    url(r'^$', views.MatchListView.as_view(), name='index'),
    url(
        r'^(?P<match_id>[0-9\-]*)/replay_parse/$',
        views.MatchReplayDetail.as_view(),
        name="replay_parse"
    ),
    url(
        r'^(?P<match_id>[0-9\-]*)/$',
        views.MatchDetail.as_view(),
        name="detail"
    ),
    url(
        r'^(?P<match_id>[0-9\-]*)/scorecard/$',
        views.MatchDetailScorecard.as_view(),
        name="detail_scorecard"
    ),
    url(
        r'^(?P<match_id>[0-9\-]*)/pickbans/$',
        views.MatchDetailPickban.as_view(),
        name="detail_pickbans"
    ),
    url(
        r'^(?P<match_id>[0-9\-]*)/abilities/$',
        views.MatchDetailAbilities.as_view(),
        name="detail_abilities"
    ),
    url(
        r'^replicate/$',
        views.ReplicateDetail.as_view(),
        name="replicate"
    ),
)
