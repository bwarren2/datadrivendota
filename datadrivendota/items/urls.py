from django.conf.urls import patterns, url
from items import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ItemIndex.as_view(), name='index'),
    url(
        r'^(?P<item_name>[a-zA-Z0-9\-\_]*)/$',
        views.ItemDetailView.as_view(),
        name='detail'
    ),
)
