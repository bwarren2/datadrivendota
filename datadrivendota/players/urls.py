from django.conf.urls import url
from players import views

urlpatterns = [
    url(r'^pros/$', views.ProIndexView.as_view(), name='pro_index'),
    url(r'^dash/$', views.DashView.as_view(), name='dash'),
    url(r'^ajax-tasks/$', views.TasksView.as_view(), name='tasks'),
    url(
        r'^(?P<player_id>[0-9]*)/$',
        views.PlayerDetailView.as_view(),
        name="id_detail"
    ),
    url(r'^$', views.PlayerIndexView.as_view(), name='index'),
]
