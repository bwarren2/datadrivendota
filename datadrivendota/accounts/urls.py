from django.conf.urls import patterns, url
from accounts import views

urlpatterns = patterns(
    '',
    url(
        r'^match-request/$',
        views.MatchRequestView.as_view(),
        name="match_request"
    ),

    url(r'^$', views.AccountsHome.as_view(), name='home'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^done/$', views.DoneView.as_view(), name='done'),
    # url(r'^ajax-auth/(?P<backend>[^/]+)/$', views.ajax_auth,
    #     name='ajax-auth'),
    url(
        r'^complete/(?P<backend>[^/]+)/$',
        views.CompleteView.as_view(),
        name='complete'
    ),
    url(r'^email-sent/', views.ValidationView.as_view(), name='email-sent'),
    url(r'^email/$', views.EmailRequiredView.as_view(), name='require_email'),
)
