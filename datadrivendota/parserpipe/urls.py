from parserpipe import views

from django.conf.urls import url

urlpatterns = [
    url(r'^dash/$', views.DashView.as_view(), name='dash'),
    url(r'^import/$', views.MatchRequestView.as_view(), name='user-import'),
    url(r'^ajax-tasks/$', views.TasksView.as_view(), name='tasks'),
    url(
        r'^ajax-import/$',
        views.MatchRequestCreateView.as_view(),
        name='import'
    ),
]
