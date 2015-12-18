from django.conf.urls import url
from accounts import views

urlpatterns = [
    url(
        r'^match-request/$',
        views.MatchRequestView.as_view(),
        name="match_request"
    ),

    url(r'^$', views.AccountsHome.as_view(), name='home'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^done/$', views.AccountsHome.as_view(), name='done'),
    url(
        r'^complete/(?P<backend>[^/]+)/$',
        views.CompleteView.as_view(),
        name='complete'
    ),
    url(r'^email-sent/', views.ValidationView.as_view(), name='email-sent'),
    url(r'^email/$', views.EmailRequiredView.as_view(), name='require_email'),
]
