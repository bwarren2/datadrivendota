from django.conf.urls import patterns, url
from items import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^winrate/$', views.ItemWinrateView.as_view(), name='winrate'),
    url(r'^(?P<item_name>[a-zA-Z0-9\-\_]*)/$', views.detail, name='detail'),
    url(
        r'^api/item-endgame/$',
        views.ApiItemEndgameChart.as_view(),
        name='api_item_endgame_chart'
        ),
)
