from base import *  # NOQA

# TEST SETTINGS
DEBUG = False
SOUTH_TESTS_MIGRATE = False

INSTALLED_APPS += (
)

# IN-MEMORY TEST DATABASE
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

# STORAGE
STATICFILES_STORAGE = 'django.core.files.storage.FileSystemStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# END STORAGE

SHOW_ACCOUNTS = True
SHOW_AUTH = True
SHOW_BLOG = True
SHOW_HEROES = True
SHOW_ITEMS = True
SHOW_LEAGUES = True
SHOW_MATCHES = True
SHOW_PAYMENTS = True
SHOW_PLAYERS = True
SHOW_SEARCH = True
SHOW_TEAMS = True
