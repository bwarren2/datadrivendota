from django.conf.urls import patterns, url
from teams import views

urlpatterns = patterns(
    '',
    url(r'^$', views.TeamList.as_view(), name='index'),
)
