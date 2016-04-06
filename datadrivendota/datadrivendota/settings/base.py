"""Common settings and globals."""

from collections import OrderedDict
from django.contrib.messages import constants as message_constants
from os.path import abspath, basename, dirname, join, normpath
from os import getenv
from sys import path
import dj_database_url

# Celery config is in the celery app, but we need this for the java parser
BROKER_URL = getenv('CLOUDAMQP_URL')

# Name and email addresses of recipients
ADMINS = (
    ("Ben Warren", "ben@datadrivendota.com"),
)

EMAIL_TIMEOUT = 10
EMAIL_PORT = getenv('MAILGUN_SMTP_PORT')
EMAIL_HOST = getenv('MAILGUN_SMTP_SERVER')
EMAIL_HOST_USER = getenv('MAILGUN_SMTP_LOGIN')
EMAIL_HOST_PASSWORD = getenv('MAILGUN_SMTP_PASSWORD')

INVOICE_FROM_EMAIL = "ben@datadrivendota.com"
ERROR_RECIPIENT_EMAIL = "ben@datadrivendota.com"

# PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
# END PATH CONFIGURATION


# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = getenv('DEBUG', False) == 'True'


# MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# END MANAGER CONFIGURATION


# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Database settings for Heroku
DATABASES = {}
DATABASES['default'] = dj_database_url.config(
    default="postgres://localhost/datadrivendota"
)
# END DATABASE CONFIGURATION


# GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/New_York'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 2

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# Bootstrap support of messages
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger',
                }
# END GENERAL CONFIGURATION

# STORAGES

# MEDIA CONFIGURATION
MEDIA_DIRECTORY = '/media/'
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

# END MEDIA CONFIGURATION


# STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))
STATIC_DIRECTORY = '/assets/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
#      #std:setting-STATICFILES_DIRS
# Note: There is a presumption that the first entry here is 'static' so that
# trash dirs work.
STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
#      #staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

#  AWS
AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = getenv('AWS_STORAGE_BUCKET_NAME', '')
AWS_QUERYSTRING_AUTH = False
AWS_IS_GZIPPED = True
GZIP_CONTENT_TYPES = ['application/json']
AWS_S3_SECURE_URLS = True
S3_URL = '//%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
DEFAULT_FILE_STORAGE = 'datadrivendota.s3utils.MediaRootS3BotoStorage'
MEDIA_URL = S3_URL + MEDIA_DIRECTORY
STATIC_URL = STATIC_DIRECTORY

#  END AWS


# END STATIC FILE CONFIGURATION


# SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = getenv('SECRET_KEY')
# END SECRET CONFIGURATION


# INTERCOM CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
INTERCOM_API_SECRET = getenv('INTERCOM_API_SECRET')
# END INTERCOM CONFIGURATION


# FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/
#      #std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
# END FIXTURE CONFIGURATION


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            normpath(join(SITE_ROOT, 'templates'))
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
                'datadrivendota.context_processors.feature_flag',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

# END TEMPLATE CONFIGURATION


# MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'payments.middleware.ActiveSubscriptionMiddleware',
)
# END MIDDLEWARE CONFIGURATION


# BEGIN CORS CONFIGURATION
CORS_ORIGIN_WHITELIST = (
    'api.intercom.io',
    'datadrivendota.s3.amazonaws.com',
    'fonts.googleapis.com',
)
# END CORS CONFIGURATION


# URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
# END URL CONFIGURATION


# APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    # 'django.contrib.admindocs',

)

THIRD_PARTY_APPS = (
    'social.apps.django_app.default',
    'blog',
    'storages',
    'bootstrapform',
    'corsheaders',
    'django_forms_bootstrap',
    'rest_framework',
    'djstripe',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'utils',
    'parserpipe',
    'heroes',
    'items',
    'players',
    'matches',
    'guilds',
    'leagues',
    'teams',
    'accounts',
    'health',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# END APP CONFIGURATION


# LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
# END LOGGING CONFIGURATION


# WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'
# END WSGI CONFIGURATION

# LOGIN CONFIGURATION
LOGIN_URL = '/login/'

AUTHENTICATION_BACKENDS = (
    'social.backends.email.EmailAuth',
    'django.contrib.auth.backends.ModelBackend',
)


# MAGIC NUMBERS
STEAM_API_KEY = getenv('STEAM_API_KEY')
# This is valve's magic number for moving between 32 and 64 bit steam ids.
ADDER_32_BIT = 76561197960265728
# This is Valve's ID for anonymized players
ANONYMOUS_ID = 4294967295
# Min length for a match to count in seconds.
MIN_MATCH_LENGTH = 600

# SOCIAL AUTH
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.get_username',
    'accounts.pipeline.require_email',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'accounts.pipeline.user_password',
    'accounts.pipeline.make_userprofile',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_STEAM_API_KEY = STEAM_API_KEY
VALID_KEY_DAYS = 7
# END LOGIN CONFIGURATION


# START REDIS CONFIGURATION
LIVE_JSON_KEY = 'live_league_json'
ITEM_SCHEMA_KEY = 'valve_item_schema_json'
# END REDIS CONFIGURATION

# Tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    #techdebt: duplicate listing here and in fabfile
    '--cover-package=parserpipe,accounts,guilds,health,heroes,items,leagues,matches,players,teams,utils,datadrivendota',
]


# START STRIPE CONFIGURATION
STRIPE_PUBLIC_KEY = getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = getenv('STRIPE_SECRET_KEY')

DJSTRIPE_PLANS = OrderedDict()

DJSTRIPE_PLANS["monthly"] = {
    "stripe_plan_id": "ddd-month",
    "name": "DDD Pro ($3/month)",
    "description": "The monthly subscription plan to DataDrivenDota",
    "price": 300,
    "interval": "month",
    "currency": "usd"
}
DJSTRIPE_PLANS["yearly"] = {
    "stripe_plan_id": "ddd-year",
    "name": "DDD Pro ($18/year)",
    "description": "The annual subscription plan to DataDrivenDota",
    "price": 1800,
    "interval": "year",
    "currency": "usd"
}

# END STRIPE CONFIGURATION

# START REST CONFIGURATION
# REST_FRAMEWORK = {
#     'PAGINATE_BY': 10
# }
# For some reason, this fucks the paginate_by = None on the viewsets
# into using a paginator.  Do not want.
# END REST CONFIGURATION

# Valve strings
HERO_BASENAME = 'npc_dota_hero_base'


KEEN_API_URL = getenv('KEEN_API_URL')
KEEN_PROJECT_ID = getenv('KEEN_PROJECT_ID')
KEEN_READ_KEY = getenv('KEEN_READ_KEY')
KEEN_WRITE_KEY = getenv('KEEN_WRITE_KEY')

# Project specific constants used in tasks
LOOKBACK_UPDATE_DAYS = 3  # The window we consider for re-checking things.
HERO_SKILL_MATCH_COUNT = 2  # How many matches to add per hero skill level
VALVE_CDN_PATH = 'http://cdn.dota2.com/apps/570/'
UPDATE_LAG_UTC = 60 * 60 * 24 * 3  # 3 Days
# We store live matches.  Wait this many minutes after storage before expecting
# Valve to have them.
LIVE_MATCH_LOOKBACK_MINUTES = 90
# If a match fails and gets to 2 days old, delete it anyway.
FAILED_LIVEMATCH_KEEP_DAYS = 2
# End project specific constants used in tasks
JAVA_QUEUE_DURABILITY = True
TESTERS = [
    103611462, 11029080, 66289584, 98193589, 85045426, 68083913, 98090295
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/accounts/email-sent/'
EMAIL_FROM = 'noreply@datadrivendota.com'

SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'accounts.mail.send_validation'

SOCIAL_AUTH_EMAIL_FORM_HTML = 'email_signup.html'
SOCIAL_AUTH_USERNAME_FORM_HTML = 'username_signup.html'
SOCIAL_AUTH_URL_NAMESPACE = 'accounts'

REPLAY_SERVICE_URL = getenv('REPLAY_SERVICE_URL')


# Blog Settings
BLOG_TITLE = "DataDrivenDota Tech Blog"
BLOG_DESCRIPTION = "Writings from the devs doing analytics"
BLOG_ENTRIES_PER_PAGE = 1
BLOG_ENTRIES_PER_RSS = 5


# Feature flagging:
SHOW_ACCOUNTS = getenv('SHOW_ACCOUNTS', False) == 'True'
SHOW_AUTH = getenv('SHOW_AUTH', False) == 'True'
SHOW_BLOG = getenv('SHOW_BLOG', False) == 'True'
SHOW_HEROES = getenv('SHOW_HEROES', False) == 'True'
SHOW_ITEMS = getenv('SHOW_ITEMS', False) == 'True'
SHOW_LEAGUES = getenv('SHOW_LEAGUES', False) == 'True'
SHOW_MATCHES = getenv('SHOW_MATCHES', False) == 'True'
SHOW_PAYMENTS = getenv('SHOW_PAYMENTS', False) == 'True'
SHOW_PLAYERS = getenv('SHOW_PLAYERS', False) == 'True'
SHOW_SEARCH = getenv('SHOW_SEARCH', False) == 'True'
SHOW_TEAMS = getenv('SHOW_TEAMS', False) == 'True'

FEATURE_FLAGS = [
    'SHOW_ACCOUNTS',
    'SHOW_AUTH',
    'SHOW_BLOG',
    'SHOW_HEROES',
    'SHOW_ITEMS',
    'SHOW_LEAGUES',
    'SHOW_MATCHES',
    'SHOW_PAYMENTS',
    'SHOW_PLAYERS',
    'SHOW_SEARCH',
    'SHOW_TEAMS',
]

SHARD_URL_BASE = (
    "https://s3.amazonaws.com/datadrivendota"
    "/processed_replay_parse/"
)
PARSER_VERSION = '1'
