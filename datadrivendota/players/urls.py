from django.conf.urls import url
from players import views

urlpatterns = [
    url(r'^pros/$', views.ProIndexView.as_view(), name='pro_index'),
    url(
        r'^(?P<player_id>[0-9]*)/$',
        views.PlayerDetailView.as_view(),
        name="id_detail"
    ),
    url(r'^$', views.PlayerIndexView.as_view(), name='index'),
]
