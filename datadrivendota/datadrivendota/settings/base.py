"""Common settings and globals."""


from os.path import abspath, basename, dirname, join, normpath
from os import getenv
from sys import path
from kombu import Exchange, Queue

import dj_database_url

#Celery
import djcelery
djcelery.setup_loader()



########## CELERY CONFIG
BROKER_POOL_LIMIT = int(getenv('BROKER_POOL_LIMIT', 1))
BROKER_URL = getenv('CLOUDAMQP_URL')

# List of modules to import when celery starts.
CELERY_IMPORTS = ("matches.management.tasks.valve_api_calls",)

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = getenv('REDISTOGO_URL')

#Stop a bazillion fake queues from being made with results.  Time in sec.
CELERY_TASK_RESULT_EXPIRES = int(getenv('RESULT_EXPIRY_RATE'))

#Only store errors.
CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

BROKER_CONNECTION_TIMEOUT = 10
CELERYD_TASK_TIME_LIMIT = 60
CELERYD_FORCE_EXECV = True

# Valve's rate limiting.
VALVE_RATE = getenv('VALVE_RATE')

CELERY_SEND_TASK_ERROR_EMAILS = True

# Name and email addresses of recipients
ADMINS = (
    ("Ben Warren", "datadrivendota@gmail.com"),
)

# Email address used as sender (From field).
SERVER_EMAIL = "celery@datadrivendota.com"


CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('api_call',  Exchange('valve_api'),   routing_key='valve_api_call'),
    Queue('db_upload',  Exchange('db'),   routing_key='db'),
)

CELERY_ROUTES = {
    'matches.management.tasks.valve_api_calls.ValveApiCall': {'exchange': 'valve_api','routing_key':'valve_api_call'},
    'matches.management.tasks.valve_api_calls.UploadMatch': {'exchange': 'db','routing_key':'db'},
    'matches.management.tasks.valve_api_calls.UpdatePlayerPersonas': {'exchange': 'db','routing_key':'db'},
    'matches.management.tasks.valve_api_calls.UploadMatchSummary': {'exchange': 'db','routing_key':'db'},
    'matches.management.tasks.valve_api_calls.RetrievePlayerRecords': {'exchange': 'default'},
    'matches.management.tasks.valve_api_calls.RefreshUpdatingPlayerRecords': {'exchange': 'default'},
}

CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_DEFAULT_QUEUE = 'default'

CELERY_ANNOTATIONS = {
    "matches.management.tasks.valve_api_calls.ValveApiCall": {"rate_limit": VALVE_RATE},
    'matches.management.tasks.valve_api_calls.UploadMatch': {'acks_late': True},
    'matches.management.tasks.valve_api_calls.UpdatePlayerPersonas': {'acks_late': True},
    'matches.management.tasks.valve_api_calls.UploadMatchSummary': {'acks_late': True},
    'matches.management.tasks.valve_api_calls.RetrievePlayerRecords': {'acks_late': True},
    'matches.management.tasks.valve_api_calls.RefreshUpdatingPlayerRecords': {'acks_late': True},
    'matches.management.tasks.valve_api_calls.AcquirePlayerData': {'acks_late': True},
    'matches.management.tasks.valve_api_calls.AcquireHeroSkillData': {'acks_late': True},

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
ADMINS = (
    ('ben', 'datadrivendota@gmail.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Database settings for Heroku
DATABASES = {}
DATABASES['default'] = dj_database_url.config(
    default='postgres://localhost/datadrivendota'
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

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
# Note: There is a presumption that the first entry here is 'static' so that trash dirs work.
STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
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


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'social_auth.context_processors.social_auth_by_type_backends',

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
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
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
    'social_auth',
    'storages',
    'djcelery',
    'pipeline'
)

# Apps specific for this project go here.
LOCAL_APPS = (
    #My custom stuff
    'heroes',
    'items',
    'players',
    'matches',
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
    'social_auth.backends.steam.SteamBackend',
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



SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    #'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('steam',)
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'associate_complete'
SOCIAL_AUTH_DEFAULT_USERNAME = 'socialauth_default_username'
SOCIAL_AUTH_EXTRA_DATA = False
SOCIAL_AUTH_CHANGE_SIGNAL_ONLY = True
SOCIAL_AUTH_ASSOCIATE_BY_EMAIL = True
########## END LOGIN CONFIGURATION


AUTO_RENDER_SELECT2_STATICS = False


########## PIPELINE CONFIGURATION
PIPELINE_CSS = {
    'all': {
        'source_filenames': (
            'css/custom_bootstrap_compilation.less',
            'js/tags/jquery.tagsinput.css',
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
            'js/jquery.metadata.js',
            'js/jquery.tablesorter.js',
            'js/jquery.tablesorter.min.js',
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
            'js/tags/jquery.tagsinput.js',
            'js/project.js',
        ),
        'output_filename': 'js/all.js',
    }
}

PIPELINE_COMPILERS = (
    'pipeline.compilers.less.LessCompiler',
)
########## END PIPELINE CONFIGURATION

