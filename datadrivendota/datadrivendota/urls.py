from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from datadrivendota import views
from accounts.views import data_applicant
from matches.views import parse_preview
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.base, name='base'),
    url(r'^blank/$', views.blank, name='blank'),
    url(r'^special/$', parse_preview, name='special'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^heroes/', include('heroes.urls', namespace='heroes')),
    url(r'^items/', include('items.urls', namespace='items')),
    url(r'^matches/', include('matches.urls', namespace='matches')),
    url(r'^players/', include('players.urls', namespace='players')),
    url(r'^leagues/', include('leagues.urls', namespace='leagues')),
    url(r'^teams/', include('teams.urls', namespace='teams')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^djs2/', include('django_select2.urls')),
    url(r'^privacy/$', views.privacy, name='privacy'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
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
    url(r'^upgrade/$', views.upgrade, name='upgrade'),
    url(r'^payments/', include("payments.urls", namespace='payments')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^blog/', include('zinnia.urls')),
     url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(
        '',
        include('social.apps.django_app.urls', namespace='social')
    ),  # Wat? Why are we including this at root? Seems risky. --kit 2014-02-16
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


