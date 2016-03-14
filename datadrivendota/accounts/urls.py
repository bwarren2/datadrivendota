from django.conf.urls import url
from accounts import views

urlpatterns = [

    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^email-sent/', views.ValidationView.as_view(), name='email-sent'),
    url(r'^email/$', views.EmailRequiredView.as_view(), name='require_email'),
    url(
        r'^forgot-password-confirm/$',
        views.ForgotPassConfirmView.as_view(),
        name='forgot_pass_confirm'
    ),
    url(
        r'^forgot-password/$',
        views.ForgotPasswordFormView.as_view(),
        name='forgot_password'
    ),
    url(
        r'^reset-password/(?P<code>[a-zA-Z0-9]+)$',
        views.ResetPasswordView.as_view(),
        name='reset_password'
    ),
    url(
        r'^complete/(?P<backend>[^/]+)/$',
        views.CompleteView.as_view(),
        name='complete'
    ),
]
