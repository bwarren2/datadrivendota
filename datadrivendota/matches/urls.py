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
    url(
        r'^match-parameter-scatter/$',
        views.MatchParameterChart.as_view(),
        name='match_parameter_scatter'
    ),
    url(
        r'^(?P<match_id>[0-9\-]*)/parse$',
        views.parse_preview,
        name="parse"
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
    url(r'^progression-sets/$',
        views.ProgressionSet.as_view(),
        name="progession_sets"),

    url(
        r'^context/$',
        views.MatchHeroContext.as_view(),
        name="match_hero_context"),
    # url(r'^overview/$', views.overview, name="overview"),
    url(r'^api/getmatches/$', views.match_list, name='match_list'),
    url(
        r'^api/endgame/$',
        views.ApiEndgameChart.as_view(),
        name='api_endgame_chart'
        ),
    url(
        r'^api/own-team-endgame/$',
        views.ApiOwnTeamEndgameChart.as_view(),
        name='api_own_team_endgame_chart'
        ),
    url(
        r'^api/same-team-endgame/$',
        views.ApiSameTeamEndgameChart.as_view(),
        name='api_same_team_endgame_chart'
        ),
    url(
        r'^api/progression/$',
        views.ApiProgressionListChart.as_view(),
        name='api_progression_chart'
        ),
    url(
        r'^api/ability-build/$',
        views.ApiAbilityBuildChart.as_view(),
        name='api_ability_build_chart'
        ),
    url(
        r'^api/set-progression/$',
        views.ApiSetProgressionChart.as_view(),
        name='api_progession_sets_chart'
        ),
    url(
        r'^api/match-scatter/$',
        views.ApiMatchScatterChart.as_view(),
        name='api_match_scatter_chart'
        ),
    url(
        r'^api/match-bar/$',
        views.ApiMatchBarChart.as_view(),
        name='api_match_bar_chart'
        ),
    url(
        r'^api/role-scatter/$',
        views.ApiRoleChart.as_view(),
        name='api_role_chart'
        ),
    url(
        r'^api/gettags/$',
        views.combobox_tags,
        name='combobox_tags'
        ),

)
