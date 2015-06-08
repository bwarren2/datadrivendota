from django.conf.urls import url, patterns
from matches import views

urlpatterns = patterns(
    '',
    url(r'^$', views.MatchListView.as_view(), name='index'),
    url(
        r'^(?P<match_id>[0-9\-]*)/parse_match/$',
        views.ParseMatchDetail.as_view(),
        name="parse_match"
    ),
    url(
        r'^(?P<match_id>[0-9\-]*)/$',
        views.MatchDetail.as_view(),
        name="match_detail"
    ),
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
        r'^api/combobox_tags/$',
        views.ComboboxAjaxView.as_view(),
        name='api_combobox'
    ),

)
