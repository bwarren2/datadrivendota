from django.conf.urls import url
from players import views

urlpatterns = [
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
]
