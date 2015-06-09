from django.conf.urls import patterns, url
from heroes import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^vitals/$', views.VitalsView.as_view(), name='vitals'),
    url(r'^lineups/$', views.LineupView.as_view(), name='lineup'),
    url(
        r'^ability/(?P<ability_name>[a-zA-Z0-9\-\_]*)/$',
        views.AbilityDetailView.as_view(),
        name='ability_detail'
    ),
    url(
        r'^(?P<hero_name>[a-zA-Z0-9\-\_]*)/$',
        views.HeroDetailView.as_view(),
        name="detail"
    ),
)
