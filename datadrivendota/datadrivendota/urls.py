"""The core urlconf."""
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from datadrivendota import views
from accounts.views import data_applicant
from rest_framework.routers import DefaultRouter
from matches.views import MatchViewSet, PlayerMatchSummaryViewSet
from teams.views import TeamViewSet
from leagues.views import LeagueViewSet
from heroes.views import HeroViewSet
from items.views import ItemViewSet
from players.views import PlayerViewSet

admin.autodiscover()

# DRF is great
router = DefaultRouter()
router.register('teams', TeamViewSet)
router.register('leagues', LeagueViewSet)
router.register('heroes', HeroViewSet)
router.register('items', ItemViewSet)
router.register('matches', MatchViewSet)
router.register('player-match-summary', PlayerMatchSummaryViewSet)
router.register('players', PlayerViewSet)

urlpatterns = patterns(
    '',
    url(r'^$', views.LandingView.as_view(), name='landing'),
    url(r'^heroes/', include('heroes.urls', namespace='heroes')),
    url(r'^items/', include('items.urls', namespace='items')),
    url(r'^matches/', include('matches.urls', namespace='matches')),
    url(r'^players/', include('players.urls', namespace='players')),
    url(r'^leagues/', include('leagues.urls', namespace='leagues')),
    url(r'^teams/', include('teams.urls', namespace='teams')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^djs2/', include('django_select2.urls')),
    url(r'^health/', include('health.urls', namespace='health')),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^upgrade/$', views.upgrade, name='upgrade'),
    url(r'^payments/', include("payments.urls")),
    url(r'^blog/', include('blog.urls', namespace='blog')),
    url(r'^rest-api/', include(router.urls, namespace='rest-api')),
    url(
        r'^data-request/$',
        data_applicant,
        name="data_applicant"
    ),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='logout'
    ),
    url(
        r'^faq/$',
        TemplateView.as_view(
            template_name='about.html',
        ),
        name='faq'
    ),
    url(
        r'^privacy/$',
        TemplateView.as_view(
            template_name='robots.txt',
        ),
        name='privacy'
    ),
    url(
        r'^robots\.txt/$',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain'
        )
    ),
    url(
        '',
        include('social.apps.django_app.urls', namespace='social')
    ),
    # Wat? Why are we including this at root? Seems risky. --kit 2014-02-16
    # Docs recommend it :/
    # https://python-social-auth.readthedocs.org/en/latest/configuration/django.html
    # Is there a better option?  --ben 2015-04-19
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
