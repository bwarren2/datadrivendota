"""The core urlconf."""
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from datadrivendota import views
from accounts.views import LoginView


# REST
from .rest_urls import router
admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^$', views.LandingView.as_view(), name='landing'),


    # Internals URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rest-api/', include(router.urls, namespace='rest-api')),
    url(r'^health/', include('health.urls', namespace='health')),

    # One-off URLs
    url(r'^blog/', include('blog.urls', namespace='blog')),

    url(
        r'^privacy/$',
        TemplateView.as_view(template_name='privacy.html',),
        name='privacy'
    ),
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
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.SHOW_LEAGUES:
    urlpatterns += patterns(
        '',
        url(r'^leagues/', include('leagues.urls', namespace='leagues')),
    )
if settings.SHOW_HEROES:
    urlpatterns += patterns(
        '',
        url(r'^heroes/', include('heroes.urls', namespace='heroes')),
    )
if settings.SHOW_ITEMS:
    urlpatterns += patterns(
        '',
        url(r'^items/', include('items.urls', namespace='items')),
    )
if settings.SHOW_MATCHES:
    urlpatterns += patterns(
        '',
        url(r'^matches/', include('matches.urls', namespace='matches')),
    )
if settings.SHOW_PLAYERS:
    urlpatterns += patterns(
        '',
        url(r'^players/', include('players.urls', namespace='players')),
    )
if settings.SHOW_TEAMS:
    urlpatterns += patterns(
        '',
        url(r'^teams/', include('teams.urls', namespace='teams')),
    )
if settings.SHOW_ACCOUNTS:
    urlpatterns += patterns(
        '',
        url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    )
if settings.SHOW_PAYMENTS:
    urlpatterns += patterns(
        '',
        url(r'^payments/', include("payments.urls")),
    )
if settings.SHOW_SEARCH:
    urlpatterns += patterns(
        '',
        url(r'^search/$', views.SearchView.as_view(), name='search'),
    )
if settings.SHOW_AUTH:
    urlpatterns += patterns(
        '',
        # When django wants a login, redir to social login
        url(r'^login/(?P<method>[^/]+)/$', LoginView.as_view(), name='login'),
        url(r'^login/$', LoginView.as_view(), name='login'),
        url(r'', include('social.apps.django_app.urls', namespace='social'))
        # Wat? Why are we including this at root? Seems risky. --kit 2014-02-16
        # Docs recommend it :/
        # https://python-social-auth.readthedocs.org/en/latest/configuration/django.html
        # Is there a better option?  --ben 2015-04-19
    )


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns(
        '',
        (
            r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {
                'document_root': settings.MEDIA_ROOT
            }
        )
    )
