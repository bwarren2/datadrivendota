"""Production settings and globals."""
from os import environ
from base import *  # NOQA

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

#          DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

MIDDLEWARE_CLASSES += (
    "datadrivendota.middleware.ForceHttps",
)

#          EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_USE_TLS = True

EMAIL_BACKEND = "sgbackend.SendGridBackend"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = getenv('smtp.sendgrid.net')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = getenv('SENDGRID_PASSWORD')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = getenv('SENDGRID_USERNAME')

SENDGRID_USER = EMAIL_HOST_USER
SENDGRID_PASSWORD = EMAIL_HOST_PASSWORD

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

DEFAULT_FROM_EMAIL = 'noreply@datadrivendota.com'
#          END EMAIL CONFIGURATION

#    Setting allowed hosts for security.  Only needed when debug = false
ALLOWED_HOSTS = (
    'datadrivendota.herokuapp.com',
    'datadrivendota.com',
    'www.datadrivendota.com',
)

#          CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
environ['MEMCACHE_SERVERS'] = environ.get(
    'MEMCACHIER_SERVERS',
    ''
).replace(',', ';')
environ['MEMCACHE_USERNAME'] = environ.get('MEMCACHIER_USERNAME', '')
environ['MEMCACHE_PASSWORD'] = environ.get('MEMCACHIER_PASSWORD', '')

CACHE_MIDDLEWARE_SECONDS = int(environ.get('CACHE_MIDDLEWARE_SECONDS', None))

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        # Use binary memcache protocol (needed for authentication)
        'BINARY': True,

        # TIMEOUT is not the connection timeout! It's the default expiration
        # timeout that should be applied to keys! Setting it to `None`
        # disables expiration.
        'TIMEOUT': environ.get('CACHE_MIDDLEWARE_SECONDS', None),
        # None is keep forever, 0 is expire immediately, else = seconds
        'OPTIONS': {
            # Enable faster IO
            'no_block': True,
            'tcp_nodelay': True,

            # Keep connection alive
            'tcp_keepalive': True,

            # Timeout for set/get requests
            '_poll_timeout': 2000,

            # Use consistent hashing for failover
            'ketama': True,

            # Configure failover timings
            'connect_timeout': 2000,
            'remove_failed': 4,
            'retry_timeout': 2,
            'dead_timeout': 10
        }
    }
}

REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_KEY_FUNC': (
        'datadrivendota.caching_keys.rest_key_constructor'
    ),
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 15,
}

#          END CACHE CONFIGURATION

# Static Files
STATIC_HOST = environ.get('DJANGO_STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/assets/'

SITE_ID = 2
