from django.conf.urls import url
from matches import views

urlpatterns = [
    url(r'^$', views.MatchListView.as_view(), name='index'),
    url(
        r'^time-lapse/$',
        views.TimeLapseDetail.as_view(),
        name="time_lapse"
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
        r'^(?P<match_id>[0-9\-]*)/replicate/$',
        views.ReplicateDetail.as_view(),
        name="replicate"
    ),
]
