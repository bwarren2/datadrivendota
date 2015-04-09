from django.conf.urls import patterns, url
from health import views

urlpatterns = patterns(
    '',
    url(r'^$', views.HealthIndexView.as_view(), name='index'),
)
