from django.conf.urls import patterns, url
from heroes import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^vitals/$', views.vitals, name='vitals'),
    url(r'^lineups/$', views.lineup, name='lineup'),
    url(r'^performance/$', views.hero_performance, name='hero_performance'),
    url(r'^skill_bars/$', views.hero_skill_bars, name='hero_skill_bars'),
    url(r'^ability/(?P<ability_name>[a-zA-Z0-9\-]*)/$', views.ability_detail, name='ability_detail'),
    url(r'^hero_performance_api/$', views.hero_performance_api, name='hero_performance_api'),
    url(r'^api/getheroes/$', views.hero_list, name='hero_list'),
    url(r'^(?P<hero_name>[a-zA-Z0-9\-]*)/$', views.detail, name="detail"),
)
