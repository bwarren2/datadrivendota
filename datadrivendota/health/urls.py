from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from health import views

urlpatterns = patterns(
    '',
    url(r'^$', views.HealthIndexView.as_view(), name='index'),
    url(
        r'^styles/$',
        TemplateView.as_view(template_name='bootstrap_test.html'),
        name='styles'
    ),
    url(r'^cards/$', views.CardIndexView.as_view(), name='cards'),
)
