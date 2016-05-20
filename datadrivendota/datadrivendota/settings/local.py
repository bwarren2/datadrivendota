"""Development settings and globals."""
from base import *  # NOQA


# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
# END DEBUG CONFIGURATION


# EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# END EMAIL CONFIGURATION

# CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': environ.get('CACHE_MIDDLEWARE_SECONDS', None),
    }
}

CACHE_ENABLED = getenv('CACHE_ENABLED', False) == 'True'
if not CACHE_ENABLED:
    CACHES['default']['backend'] = (
        'django.core.cache.backends.dummy.DummyCache'
    )
# END CACHE CONFIGURATION


# TOOLBAR CONFIGURATION
# See: https://github.com/django-debug-toolbar/django-debug-toolbar/
#      #installation
INSTALLED_APPS += (
    'debug_toolbar',
    'debug_toolbar_line_profiler',
    'template_profiler_panel',
)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar/
#      #installation
INTERNAL_IPS = ('127.0.0.1',)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar/
#      #installation
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
# END TOOLBAR CONFIGURATION

# STATIC CONFIGURATION
STATIC_URL = '/assets/'
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

MEDIA_URL = '/media/'
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


DEVSERVER_MODULES = (
    'devserver.modules.profile.ProfileSummaryModule',

    # Modules not enabled by default
    'devserver.modules.profile.LineProfilerModule',
)

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False
}

DEVSERVER_AUTO_PROFILE = True


DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar_line_profiler.panel.ProfilingPanel',
    'template_profiler_panel.panels.template.TemplateProfilerPanel',
)
