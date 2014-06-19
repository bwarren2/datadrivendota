from django.conf.urls import patterns, url
from leagues import views

urlpatterns = patterns(
    '',
    url(r'^$', views.LeagueList.as_view(), name='index'),
)
