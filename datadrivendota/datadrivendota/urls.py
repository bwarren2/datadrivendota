from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from datadrivendota import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.base, name='base'),
    url('', include('social.apps.django_app.urls', namespace='social')), # Wat? --kit 2013-10-27
    url(r'^about/$', views.about, name='about'),
    url(r'^heroes/', include('heroes.urls', namespace='heroes')),
    url(r'^items/', include('items.urls', namespace='items')),
    url(r'^matches/', include('matches.urls', namespace='matches')),
    url(r'^players/', include('players.urls', namespace='players')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^djs2/', include('django_select2.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='logout'
    ),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
