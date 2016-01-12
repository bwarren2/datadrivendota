from parserpipe import views

from django.conf.urls import url

urlpatterns = [
    url(r'^dash/$', views.DashView.as_view(), name='dash'),
    url(r'^tasks/$', views.TasksView.as_view(), name='tasks'),
]
