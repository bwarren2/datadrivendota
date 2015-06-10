from django.conf.urls import url, patterns
from matches import views

urlpatterns = patterns(
    '',
    url(r'^$', views.MatchListView.as_view(), name='index'),
    url(
        r'^(?P<match_id>[0-9\-]*)/parse_match/$',
        views.ParseMatchDetail.as_view(),
        name="parse_match"
    ),
    url(
        r'^(?P<match_id>[0-9\-]*)/$',
        views.MatchDetail.as_view(),
        name="match_detail"
    ),
    url(
        r'^api/combobox_tags/$',
        views.ComboboxAjaxView.as_view(),
        name='api_combobox'
    ),

)
