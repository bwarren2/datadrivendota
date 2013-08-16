from django.conf.urls import url, patterns
from matches import views

urlpatterns = patterns('',
    url(r'^/?$', views.index, name='index'),
    url(r'^endgame/?$', views.endgame, name='endgame')
)
