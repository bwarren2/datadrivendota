from django.conf.urls import patterns, url
from accounts import views

urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.player_management,
        name="management",
    ),
    url(
        r'^match-request/$',
        views.MatchRequestView.as_view(),
        name="match_request"
    ),
    url(
        r'^tracking/$',
        views.TrackingView.as_view(),
        name="tracking"
    ),
    url(
        r'^following/$',
        views.FollowView.as_view(),
        name="following"
    ),
    url(r'^api/dropfollow/$', views.drop_follow, name='drop_follow'),
    url(r'^api/checkid/$', views.check_id, name='check_id'),
    url(r'^api/addtrack/$', views.add_track, name='add_track'),
    url(
        r'^poll/$',
        views.PollView.as_view(),
        name="poll"
    ),
)
