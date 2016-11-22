"""The core urlconf."""
from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from datadrivendota import views
from accounts.views import LoginView, LogoutView
from matches.viewsets import ParseShardView

# REST
from .rest_urls import router
admin.autodiscover()


urlpatterns = [
    url(r'^$', views.LandingView.as_view(), name='landing'),

    # Internals URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rest-api/', include(router.urls, namespace='rest-api')),
    url(
        r'^rest-api/parse-shards',
        ParseShardView.as_view(),
        name='parse-shards'
    ),
    url(r'^health/', include('health.urls', namespace='health')),

    # One-off URLs
    url(r'^blog/', include('blog.urls', namespace='blog')),

    url(
        r'^privacy/$',
        TemplateView.as_view(template_name='privacy.html',),
        name='privacy'
    ),
    # Even if we don't want users to login, SUs need to be able to log out.
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^.well-known/acme-challenge/AIj9I3G0D31Mc_CJYBJWUxJlySJ0mQYRvVQkfRUFrv0$',
        TemplateView.as_view(
            template_name='acme.txt',
            content_type='text/plain'
        ),
        name='acme'),
    url(
        r'^api/combobox_tags/$',
        views.ComboboxAjaxView.as_view(),
        name='api_combobox'
    ),
    url(
        r'^robots\.txt/$',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain'
        )
    ),
    url(r'^parserpipe/', include('parserpipe.urls', namespace='parserpipe')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.SHOW_LEAGUES:
    urlpatterns += [
        url(r'^leagues/', include('leagues.urls', namespace='leagues')),
    ]
if settings.SHOW_HEROES:
    urlpatterns += [
        url(r'^heroes/', include('heroes.urls', namespace='heroes')),
    ]
if settings.SHOW_ITEMS:
    urlpatterns += [
        url(r'^items/', include('items.urls', namespace='items')),
    ]
if settings.SHOW_MATCHES:
    urlpatterns += [
        url(r'^matches/', include('matches.urls', namespace='matches')),
    ]
if settings.SHOW_PLAYERS:
    urlpatterns += [
        url(r'^players/', include('players.urls', namespace='players')),
    ]
if settings.SHOW_TEAMS:
    urlpatterns += [
        url(r'^teams/', include('teams.urls', namespace='teams')),
    ]
if settings.SHOW_ACCOUNTS:
    urlpatterns += [
        url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    ]
if settings.SHOW_PAYMENTS:
    urlpatterns += [
        url(r'^payments/', include('djstripe.urls', namespace="djstripe")),
    ]
if settings.SHOW_SEARCH:
    urlpatterns += [
        url(r'^search/$', views.SearchView.as_view(), name='search'),
    ]
if settings.SHOW_AUTH:
    urlpatterns += [
        # When django wants a login, redir to social login
        # url(r'^login/(?P<method>[^/]+)/$', LoginView.as_view(), name='login'),
        # url(r'^login/$', LoginView.as_view(), name='login'),
        url(r'', include('social.apps.django_app.urls', namespace='social'))
    ]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        url(
            r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {
                'document_root': settings.MEDIA_ROOT
            }
        )
    ]
