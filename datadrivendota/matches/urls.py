from django.conf.urls import url, patterns
from matches import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^endgame/$', views.endgame, name='endgame'),
    url(r'^(?P<match_id>[0-9\-]*)/$', views.match, name="match_detail")

)
