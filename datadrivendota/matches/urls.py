from django.conf.urls import url, patterns
from matches import views

urlpatterns = patterns(
    '',
    url(r'^$', views.follow_match_feed, name='index'),
    url(r'^follow-matches/$', views.follow_match_feed, name='follow_index'),
    url(
        r'^endgame/$',
        views.Endgame.as_view(),
        name='endgame'
    ),
    url(
        r'^team-endgame/$',
        views.SameTeamEndgame.as_view(),
        name='team_endgame'
    ),
    url(
        r'^own-team-endgame/$',
        views.OwnTeamEndgame.as_view(),
        name='own_team_endgame'
    ),
    url(r'^(?P<match_id>[0-9\-]*)/$', views.match, name="match_detail"),
    url(
        r'^ability-build/$',
        views.AbilityBuild.as_view(),
        name="ability_build"
    ),
    url(r'^progression-list/$',
        views.ProgressionList.as_view(),
        name="progession_list"),
    url(r'^overview/$', views.overview, name="overview"),
    url(r'^api/getmatches/$', views.match_list, name='match_list'),

)
