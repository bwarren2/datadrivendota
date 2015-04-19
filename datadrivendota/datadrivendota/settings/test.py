from base import *

########## TEST SETTINGS
DEBUG = False
TEMPLATE_DEBUG = False
SOUTH_TESTS_MIGRATE = False

INSTALLED_APPS += (
    # 'django_nose',
    # 'django_behave',
)

# TEST_RUNNER = 'django_behave.runner.DjangoBehaveTestSuiteRunner'

########## IN-MEMORY TEST DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

VERBOSE_PROFILING = False
