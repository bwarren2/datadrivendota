from django.conf.urls import patterns, url
from health import views

urlpatterns = patterns(
    '',
    url(r'^$', views.HealthIndexView.as_view(), name='index'),
    url(r'^styles/$', views.StylesIndexView.as_view(), name='styles'),
    url(r'^cards/$', views.CardIndexView.as_view(), name='cards'),
)
