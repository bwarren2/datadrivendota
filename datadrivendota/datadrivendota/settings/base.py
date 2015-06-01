"""Common settings and globals."""


from django.contrib.messages import constants as message_constants
from os.path import abspath, basename, dirname, join, normpath
from os import getenv
from sys import path

import dj_database_url

# Celery config is in the celery app

# Name and email addresses of recipients
ADMINS = (
    ("Ben Warren", "ben@datadrivendota.com"),
)

EMAIL_PORT = getenv('MAILGUN_SMTP_PORT')
EMAIL_TIMEOUT = 10
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

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
# END DEBUG CONFIGURATION


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
STATICFILES_STORAGE = 'datadrivendota.s3utils.S3PipelineCachedStorage'
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
    'pipeline.finders.PipelineFinder',
)

#  AWS
AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = getenv('AWS_STORAGE_BUCKET_NAME', '')
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = True
S3_URL = '//%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

MEDIA_URL = S3_URL + MEDIA_DIRECTORY
STATIC_URL = S3_URL + STATIC_DIRECTORY

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


# TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/
#      #template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    # 'social_auth.context_processors.social_auth_by_type_backends',

)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    normpath(join(SITE_ROOT, 'templates')),
)
# END TEMPLATE CONFIGURATION


# MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
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
    'storages',
    'pipeline',
    'bootstrapform',
    'corsheaders',
    'payments',
    'django_forms_bootstrap',
    'tagging',
    'mptt',
    'rest_framework',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'utils',
    'heroes',
    'items',
    'players',
    'matches',
    'guilds',
    'leagues',
    'teams',
    'accounts',
    'health',
    'blog',
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
    'social.backends.steam.SteamOpenId',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'

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
    'social.pipeline.user.get_username',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'players.pipeline.create_player',
)


SOCIAL_AUTH_STEAM_API_KEY = STEAM_API_KEY
VALID_KEY_DAYS = 7
# END LOGIN CONFIGURATION


AUTO_RENDER_SELECT2_STATICS = False


# PIPELINE CONFIGURATION
PIPELINE_CSS = {
    'project': {
        'source_filenames': (
            'css/release.css',
        ),
        'output_filename': 'css/all.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'third_party': {
        'source_filenames': (
            'css/bootstrap-tour.css',
            'jquery-ui-bootstrap/jquery-ui-1.10.0.custom.css',
            'select2-3.4.5/select2.css',
            'select2-3.4.5/select2-bootstrap.css',
            'messenger/messenger.css',
            'messenger/messenger-theme-future.css',
        ),
        'output_filename': 'css/others.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },



}

PIPELINE_JS = {
    'all': {
        'source_filenames': (
            'js/jquery-ui.js',
            'js/jquery.metadata.js',
            'js/jquery.tablesorter.js',
            'messenger/messenger.js',
            'messenger/messenger-theme-future.js',
            'bootstrap/js/transition.js',
            'bootstrap/js/modal.js',
            'bootstrap/js/dropdown.js',
            'bootstrap/js/scrollspy.js',
            'bootstrap/js/tab.js',
            'bootstrap/js/tooltip.js',
            'bootstrap/js/popover.js',
            'bootstrap/js/alert.js',
            'bootstrap/js/button.js',
            'bootstrap/js/collapse.js',
            'bootstrap/js/carousel.js',
            'bootstrap/js/affix.js',
            'js/bootstrap-tour.js',
            'select2-3.4.5/select2.js',
            'js/d3/d3.min.js',
            'js/eldarion-ajax.js',
            'js/charting.js',
            'js/gunzip.min.js',
            'js/project.js',
        ),
        'output_filename': 'js/all.js',
    },
    'jquery': {
        'source_filenames': (
            'js/jquery-1.10.2.js',
        ),
        'output_filename': 'js/jq.js',
    },
    'bluebird': {
        'source_filenames': (
            'js/bluebird.min.js',
        ),
        'output_filename': 'js/bluebird.js',
    },
    'handlebars': {
        'source_filenames': (
            'js/handlebars.js',
        ),
        'output_filename': 'js/handlebars.js',
    }
}

PIPELINE_COMPILERS = (
    'pipeline.compilers.less.LessCompiler',
)

# END PIPELINE CONFIGURATION


# START REDIS CONFIGURATION
LIVE_JSON_KEY = 'live_league_json'
ITEM_SCHEMA_KEY = 'valve_item_schema_json'
# END REDIS CONFIGURATION

# Tests
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# NOSE_ARGS = [
#     '--with-coverage',
# ]


# Magic Colors
DIRE_RED = '#BA3B15'
RADIANT_GREEN = '#7CD51B'
WON_COLOR = '#FFD700'
LOST_COLOR = '#C0C0C0'
STRENGTH_COLOR = '#CC5240'
AGILITY_COLOR = '#4BAA49'
INTELLIGENCE_COLOR = '#618ABE'
SKILL1_COLOR = '#CC0000'
SKILL2_COLOR = '#CCAF00'
SKILL3_COLOR = '#3ACC00'
SKILLPLAYER_COLOR = '#00CC75'
SKILLTOURNAMENT_COLOR = '#AA37CA'
CONTRASTING_10 = [
    '#1f77b4',
    '#7EF6C6',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf',
]
PLAYER_10 = [
    '#1f77b4',
    '#7EF6C6',
    '#9A1D9B',
    '#ECF14C',
    '#DB7226',
    '#E890BA',
    '#99B15F',
    '#75D1E1',
    '#147335',
    '#906A2B',
]

# START STRIPE CONFIGURATION
STRIPE_SECRET_KEY = getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = getenv('STRIPE_PUBLIC_KEY')

PAYMENTS_PLANS = {
    "monthly": {
        "stripe_plan_id": "ddd-month",
        "name": "DDD Pro ($3/month)",
        "description": "The monthly subscription plan to DataDrivenDota",
        "price": 3,
        "interval": "month",
        "currency": "usd"
    },
    "annually": {
        "stripe_plan_id": "ddd-year",
        "name": "DDD Pro ($30/year)",
        "description": "The annual subscription plan to DataDrivenDota",
        "price": 30,
        "interval": "year",
        "currency": "usd"
    }
}

SUBSCRIPTION_REQUIRED_EXCEPTION_URLS = [
    'heroes:index',
    'payments_subscribe',
]

SUBSCRIPTION_REQUIRED_REDIRECT = 'payments_subscribe'
# END STRIPE CONFIGURATION

TI4_TEAMS = [
    1333179,
    999689,
    15,
    26,
    5,
    7,
    726228,
    39,
    111474,
    36,
    350190,
    46,
    26,
    1375614,
    1642908,
]


# START REST CONFIGURATION
# REST_FRAMEWORK = {
#     'PAGINATE_BY': 10
# }
# For some reason, this fucks the paginate_by = None on the viewsets
# into using a paginator.  Do not want.
# END REST CONFIGURATION

# Valve strings
HERO_BASENAME = 'npc_dota_hero_base'


BLANK_ITEM_THUMBSHOT = (
    "https://s3.amazonaws.com/datadrivendota/blanks/"
    "blank_item_thumbshot.png"
)

BLANK_ITEM_MUGSHOT = (
    "https://s3.amazonaws.com/datadrivendota/"
    "blanks/blank_item.png"
)

BLANK_LEAGUE_IMAGE = (
    'https://s3.amazonaws.com/datadrivendota/'
    'blanks/blank_league.png'
)

BLANK_TEAM_IMAGE = (
    "https://s3.amazonaws.com/datadrivendota/"
    "blanks/blank_team.png"
)

KEEN_API_URL = getenv('KEEN_API_URL')
KEEN_PROJECT_ID = getenv('KEEN_PROJECT_ID')
KEEN_READ_KEY = getenv('KEEN_READ_KEY')
KEEN_WRITE_KEY = getenv('KEEN_WRITE_KEY')

# Project specific constants used in tasks
LOOKBACK_UPDATE_DAYS = 3  # The window we consider for re-checking things.
HERO_SKILL_MATCH_COUNT = 3  # How many matches to add per hero skill level
CLIENT_MATCH_COUNT = 3  # How many client matches to get each pull
VALVE_CDN_PATH = 'http://cdn.dota2.com/apps/570/'
UPDATE_LAG_UTC = 60 * 60 * 24 * 3  # 3 Days
# End project specific constants used in tasks
