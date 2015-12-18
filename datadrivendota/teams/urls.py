from django.conf.urls import url
from teams import views

urlpatterns = [
    url(r'^$', views.TeamList.as_view(), name='index'),
    url(
        r'^(?P<steam_id>[0-9\-]*)/$',
        views.TeamDetail.as_view(),
        name='detail'
    ),
]
