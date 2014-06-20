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
)
