from django.conf.urls import patterns, url
from teams import views

urlpatterns = patterns(
    '',
    url(r'^$', views.TeamList.as_view(), name='index'),
    url(
        r'^(?P<steam_id>[0-9\-]*)/$',
        views.TeamDetail.as_view(),
        name='detail'
    ),
)
