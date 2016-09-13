from django.conf.urls import url
from matches import views

urlpatterns = [
    url(r'^$', views.MatchListView.as_view(), name='index'),
    url(
        r'mine/$',
        views.MyMatchListView.as_view(),
        name='index-mine',
    ),
    url(
        r'^parsed/$',
        views.ParsedMatchListView.as_view(),
        name='parsed_index'
    ),
    url(
        r'^analytic-charts/$',
        views.AnalyticChartsView.as_view(),
        name="time_lapse"
    ),
    url(
        r'^versus-charts/$',
        views.VersusChartsView.as_view(),
        name="duel"
    ),
    url(
        r'^replay-overlay/$',
        views.ReplayOverlayView.as_view(),
        name="ghostwalk"
    ),
    url(
        r'^replay/(?P<match_id>[0-9\-]*)/$',
        views.ReplayView.as_view(),
        name="legacy-replay"
    ),  # Legacy for the dev forums for 2wks
    url(
        r'^(?P<match_id>[0-9\-]*)/replay/$',
        views.ReplayView.as_view(),
        name="replay"
    ),  # Matching the rest of the url formatting
    url(
        r'^performance/$',
        views.PerformanceView.as_view(),
        name="performance"
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
        r'^(?P<match_id>[0-9\-]*)/parsed-detail/$',
        views.MatchParsedDetail.as_view(),
        name="detail_parsed"
    ),
]
