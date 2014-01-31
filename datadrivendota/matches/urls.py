from django.conf.urls import url, patterns
from matches import views

urlpatterns = patterns(
    '',
    url(r'^$', views.follow_match_feed, name='index'),
    url(r'^follow-matches/$', views.follow_match_feed, name='follow_index'),
    url(r'^endgame/$', views.endgame, name='endgame'),
    url(r'^team-endgame/$', views.team_endgame, name='team_endgame'),
    url(r'^(?P<match_id>[0-9\-]*)/$', views.match, name="match_detail"),
    url(r'^ability-build/$', views.ability_build, name="ability_build"),
    url(r'^overview/$', views.overview, name="overview")

)

