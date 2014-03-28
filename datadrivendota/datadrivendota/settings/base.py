"""Common settings and globals."""


from os.path import abspath, basename, dirname, join, normpath
from os import getenv
from sys import path
from kombu import Exchange, Queue

import dj_database_url

#Celery
########## CELERY CONFIG
BROKER_POOL_LIMIT = int(getenv('BROKER_POOL_LIMIT', 1))
BROKER_URL = getenv('CLOUDAMQP_URL')
BROKER_CONNECTION_TIMEOUT = int(getenv('BROKER_CONNECTION_TIMEOUT'))
BROKER_CONNECTION_RETRY = True
CELERYD_CONCURRENCY = int(getenv('CELERYD_CONCURRENCY'))
# List of modules to import when celery starts.
CELERY_IMPORTS = ("matches.management.tasks.valve_api_calls",)

## What happens if we do not use redis?.
CELERY_RESULT_BACKEND = getenv('REDISTOGO_URL')

#Stop a bazillion fake queues from being made with results.  Time in sec.
CELERY_TASK_RESULT_EXPIRES = int(getenv('RESULT_EXPIRY_RATE'))

#Only store errors.
#NOTE: this means that you cannot get the results of the tasks.
CELERY_IGNORE_RESULT = getenv('CELERY_IGNORE_RESULT') == 'True'
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

CELERYD_TASK_TIME_LIMIT = int(getenv('CELERYD_TASK_TIME_LIMIT'))
CELERY_ACKS_LATE = True

#Experimenting
CELERYD_TASK_SOFT_TIME_LIMIT = 59

CELERY_REDIS_MAX_CONNECTIONS = int(getenv('CELERY_REDIS_MAX_CONNECTIONS'))

# Valve's rate limiting.
VALVE_RATE = getenv('VALVE_RATE')

CELERY_SEND_TASK_ERROR_EMAILS = True

# Name and email addresses of recipients
ADMINS = (
    ("Ben Warren", "ben@datadrivendota.com"),
)

# Email address used as sender (From field).
SERVER_EMAIL = "celery@datadrivendota.com"


CELERY_QUEUES = (
    Queue('management', Exchange('management'), routing_key='management'),
    Queue('api_call',  Exchange('valve_api'),   routing_key='valve_api_call'),
    Queue('db_upload',  Exchange('db'),   routing_key='db'),
    Queue('rpr',  Exchange('rpr'),   routing_key='rpr'),
)

CELERY_ROUTES = {
    'matches.management.tasks.valve_api_calls.ValveApiCall': {
        'exchange': 'valve_api',
        'routing_key': 'valve_api_call',
    },
    'matches.management.tasks.valve_api_calls.RetrievePlayerRecords': {
        'exchange': 'rpr',
        'routing_key': 'rpr',
    },
    'matches.management.tasks.valve_api_calls.UploadMatch': {
        'exchange': 'db',
        'routing_key': 'db',
    },
    'matches.management.tasks.valve_api_calls.RefreshUpdatePlayerPersonas': {
        'exchange': 'management',
        'routing_key': 'management',
    },
    'matches.management.tasks.valve_api_calls.UpdatePlayerPersonas': {
        'exchange': 'db',
        'routing_key': 'db',
    },
    'matches.management.tasks.valve_api_calls.RefreshPlayerMatchDetail': {
        'exchange': 'management',
        'routing_key': 'management',
    },
    'matches.management.tasks.valve_api_calls.AcquirePlayerData': {
        'exchange': 'management',
        'routing_key': 'management',
    },
    'matches.management.tasks.valve_api_calls.AcquireHeroSkillData': {
        'exchange': 'management',
        'routing_key': 'management',
    },

}

CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_DEFAULT_QUEUE = 'default'

CELERY_ANNOTATIONS = {
    "matches.management.tasks.valve_api_calls.ValveApiCall": {
        "rate_limit": VALVE_RATE,
        'acks_late': True,
        'max_retries': 5,
    },
    'matches.management.tasks.valve_api_calls.RetrievePlayerRecords': {
        'acks_late': True,
        'max_retries': 5,
    },
    'matches.management.tasks.valve_api_calls.UploadMatch': {
        'acks_late': True,
        'max_retries': 5,
    },
    'matches.management.tasks.valve_api_calls.RefreshUpdatePlayerPersonas': {
        'acks_late': True,
        'max_retries': 5,
    },
    'matches.management.tasks.valve_api_calls.UpdatePlayerPersonas': {
        'acks_late': True,
        'max_retries': 5,
    },
    'matches.management.tasks.valve_api_calls.RefreshPlayerMatchDetail': {
        'acks_late': True,
        'max_retries': 5,
    },
    'matches.management.tasks.valve_api_calls.AcquirePlayerData': {
        'acks_late': True,
        'max_retries': 5,
    },
    'matches.management.tasks.valve_api_calls.AcquireHeroSkillData': {
        'acks_late': True,
        'max_retries': 5,
    },

}

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = getenv('DEBUG', False) == 'True'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Database settings for Heroku
DATABASES = {}
DATABASES['default'] = dj_database_url.config(
    default="postgres://localhost/datadrivendota"
)
########## END DATABASE CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/Los_Angeles'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
########## END GENERAL CONFIGURATION

####STORAGES####
AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = getenv('AWS_STORAGE_BUCKET_NAME', '')
DEFAULT_FILE_STORAGE = 'datadrivendota.s3utils.MediaRootS3BotoStorage'
AWS_QUERYSTRING_AUTH = False
S3_URL = 'http://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_DIRECTORY = '/assets/'
MEDIA_DIRECTORY = '/media/'


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = S3_URL + MEDIA_DIRECTORY
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = S3_URL + STATIC_DIRECTORY

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

STATICFILES_STORAGE = 'datadrivendota.s3utils.S3PipelineStorage'

########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = getenv('SECRET_KEY')
########## END SECRET CONFIGURATION


########## INTERCOM CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
INTERCOM_API_SECRET = getenv('INTERCOM_API_SECRET')
########## END INTERCOM CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/
#      #std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
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
    'zinnia.context_processors.version',  # Optional

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
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
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
    #'payments.middleware.ActiveSubscriptionMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## BEGIN CORS CONFIGURATION
CORS_ORIGIN_WHITELIST = (
    'api.intercom.io',
    'datadrivendota.s3.amazonaws.com',
    'fonts.googleapis.com',
)
########## END CORS CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.comments',
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
    # Database migration helpers:
    'south',
    'social.apps.django_app.default',
    'storages',
    'pipeline',
    'bootstrapform',
    'corsheaders',
    'payments',
    'django_forms_bootstrap',
    'tagging',
    'mptt',
    'zinnia',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    #My custom stuff
    'utils',
    'heroes',
    'items',
    'players',
    'matches',
    'guilds',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
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
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'
########## END WSGI CONFIGURATION

########## LOGIN CONFIGURATION
LOGIN_URL = '/login/'

AUTHENTICATION_BACKENDS = (
    'social.backends.steam.SteamOpenId',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'

###############MAGIC NUMBERS
STEAM_API_KEY = getenv('STEAM_API_KEY')
# This is valve's magic number for moving between 32 and 64 bit steam ids.
ADDER_32_BIT = 76561197960265728
#This is Valve's ID for anonymized players
ANONYMOUS_ID = 4294967295
#Min length for a match to count in seconds.
MIN_MATCH_LENGTH = 600


###############SOCIAL AUTH
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
########## END LOGIN CONFIGURATION


AUTO_RENDER_SELECT2_STATICS = False


########## PIPELINE CONFIGURATION
PIPELINE_CSS = {
    'all': {
        'source_filenames': (
            'css/custom_bootstrap_compilation.less',
            'css/bootstrap-tour.less',
            'jquery-ui-bootstrap/jquery-ui-1.10.0.custom.css',
            'select2-3.4.5/select2.css',
            'select2-3.4.5/select2-bootstrap.css',
            'messenger/messenger.css',
            'messenger/messenger-theme-future.css',
            'css/project.less'
        ),
        'output_filename': 'css/all.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
}

PIPELINE_JS = {
    'all': {
        'source_filenames': (
            'js/jquery-1.10.2.js',
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
            'js/eldarion-ajax.full.js',
            'js/charting.js',
            'js/project.js',
        ),
        'output_filename': 'js/all.js',
    }
}

PIPELINE_COMPILERS = (
    'pipeline.compilers.less.LessCompiler',
)
########## END PIPELINE CONFIGURATION

# Tests
# Thorny!
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--with-yanc', '--stop']


#Magic Colors
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
CONTRASTING_10 = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf',
]

#Stripe
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
    'payments:payments_subscribe',
    ]

SUBSCRIPTION_REQUIRED_REDIRECT = 'payments:payments_subscribe'
