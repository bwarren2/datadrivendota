from django.conf.urls import patterns, url
from players import views

urlpatterns = patterns(
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
)
