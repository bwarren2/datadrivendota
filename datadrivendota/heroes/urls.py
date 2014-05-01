from django.conf.urls import patterns, url
from heroes import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^vitals/$', views.Vitals.as_view(), name='vitals'),
    url(r'^lineups/$', views.Lineup.as_view(), name='lineup'),
    url(r'^performance/$',
        views.HeroPerformance.as_view(),
        name='hero_performance'),
    url(
        r'^performance-lineup/$',
        views.HeroPerformanceLineup.as_view(),
        name='hero_performance_lineup'
    ),
    url(r'^skillbuild_winrate/$',
        views.HeroBuildLevel.as_view(),
        name='hero_skill_bars',
        ),
    url(
        r'^skill_progression/$',
        views.HeroSkillProgression.as_view(),
        name='hero_skill_progression'
    ),
    url(
        r'^ability/(?P<ability_name>[a-zA-Z0-9\-\_]*)/$',
        views.ability_detail,
        name='ability_detail'
    ),
    url(
        r'^api/vitals_chart$',
        views.ApiVitalsChart.as_view(),
        name='api_vitals_chart'
    ),
    url(
        r'^api/lineup_chart$',
        views.ApiLineupChart.as_view(),
        name='api_lineup_chart'
    ),
    url(
        r'^api/skill_progression_chart$',
        views.ApiSkillProgressionChart.as_view(),
        name='api_skill_progression_chart'
    ),
    url(
        r'^api/build_level_chart$',
        views.ApiBuildLevelChart.as_view(),
        name='api_build_level_chart'
    ),
    url(
        r'^api/hero_performance_chart$',
        views.ApiHeroPerformanceChart.as_view(),
        name='api_hero_performance_chart'
    ),
    url(
        r'^api/update_player_winrate$',
        views.ApiUpdatePlayerWinrateChart.as_view(),
        name='api_update_player_winrate_chart'
    ),
    url(
        r'^api/hero_performance_lineup$',
        views.ApiHeroPerformanceLineupChart.as_view(),
        name='api_hero_performance_lineup_chart'
    ),

    url(r'^api/getheroes/$', views.hero_list, name='hero_list'),
    url(r'^(?P<hero_name>[a-zA-Z0-9\-\_]*)/$', views.detail, name="detail"),
)
