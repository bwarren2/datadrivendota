from django.conf.urls import url, patterns
from matches import views

urlpatterns = patterns(
    '',
    url(r'^$', views.MatchListView.as_view(), name='index'),
    url(
        r'^(?P<match_id>[0-9\-]*)/replay_parse/$',
        views.MatchReplayDetail.as_view(),
        name="replay_parse"
    ),  # Transitioning to this version
    url(
        r'^(?P<match_id>[0-9\-]*)/$',
        views.MatchDetail.as_view(),
        name="detail"
    ),
    url(
        r'^api/combobox_tags/$',
        views.ComboboxAjaxView.as_view(),
        name='api_combobox'
    ),

)
