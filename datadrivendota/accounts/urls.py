from django.conf.urls import patterns, url
from accounts import views

urlpatterns = patterns(
    '',
    url(
        r'^match-request/$',
        views.MatchRequestView.as_view(),
        name="match_request"
    ),
)
