from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from datadrivendota import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', views.base, name='base'),
    url(r'^about/?$', views.about, name='about'),
    url(r'^heroes/?', include('heroes.urls')),
    url(r'^items/?', include('items.urls')),
    url(r'^matches/?', include('matches.urls')),
    url(r'^players/?', include('players.urls')),

    #url(r'^/?$', TemplateView.as_view(template_name='base.html')),
    # Examples:
    # url(r'^$', 'datadrivendota.views.home', name='home'),
    # url(r'^datadrivendota/', include('datadrivendota.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social_auth.urls')),
    url(r'^djs2/', include('django_select2.urls')),
    url(r'^login/?', 'django.contrib.auth.views.login'),
    url(r'^logout/?', 'django.contrib.auth.views.logout', {'next_page': '/'})
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

