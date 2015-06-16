from django.conf.urls import patterns, url
from players import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ProIndexView.as_view(), name='pro_index'),
    url(
        r'^(?P<player_id>[0-9]*)/$',
        views.PlayerDetailView.as_view(),
        name="id_detail"
    ),
    url(
        r'^followed/$',
        views.FollowedPlayerIndexView.as_view(),
        name='followed_index'
    ),
    url(r'^all-players/$', views.PlayerIndexView.as_view(), name='index'),
    url(
        r'^hero-style/(?P<player_id>[0-9]*)-(?P<hero_name>[a-zA-Z0-9\-]*)$',
        views.HeroStyleView.as_view(),
        name='hero_style'
    ),
)
