from __future__ import absolute_import
from os import getenv
from kombu import Exchange, Queue
from django.conf import settings
from datetime import timedelta
from celery import Celery

app = Celery('datadrivendota')


class Config(object):
    BROKER_POOL_LIMIT = int(getenv('BROKER_POOL_LIMIT', 1))
    BROKER_URL = getenv('CLOUDAMQP_URL')
    BROKER_CONNECTION_TIMEOUT = int(getenv('BROKER_CONNECTION_TIMEOUT'))
    BROKER_CONNECTION_RETRY = True
    CELERYD_CONCURRENCY = int(getenv('CELERYD_CONCURRENCY'))
    # List of modules to import when celery starts.
    CELERY_IMPORTS = (
        "matches.management.tasks",
        "items.management.tasks",
        "heroes.management.tasks",
        "players.management.tasks",
        "leagues.management.tasks",
        "teams.management.tasks",
        "datadrivendota.management.tasks",
        )

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
    CELERYD_TASK_SOFT_TIME_LIMIT = int(getenv('CELERYD_TASK_SOFT_TIME_LIMIT'))

    CELERY_REDIS_MAX_CONNECTIONS = int(getenv('CELERY_REDIS_MAX_CONNECTIONS'))

    # Valve's rate limiting.
    VALVE_RATE = getenv('VALVE_RATE')

    ADMINS = settings.ADMINS

    CELERY_SEND_TASK_ERROR_EMAILS = True
    EMAIL_PORT = settings.EMAIL_PORT
    EMAIL_TIMEOUT = settings.EMAIL_TIMEOUT
    EMAIL_HOST = settings.EMAIL_HOST
    EMAIL_HOST_USER = settings.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD

    #Where celery emails from.
    SERVER_EMAIL = "celery@datadrivendota.com"

    CELERY_QUEUES = (
        Queue(
            'management',
            Exchange('management'),
            routing_key='management'
        ),
        Queue(
            'api_call',
            Exchange('valve_api'),
            routing_key='valve_api_call'
        ),
        Queue(
            'db_upload',
            Exchange('db'),
            routing_key='db'
        ),
        Queue(
            'rpr',
            Exchange('rpr'),
            routing_key='rpr'
        ),
    )

    CELERY_ROUTES = {
        'datadrivendota.management.tasks.ValveApiCall': {
            'exchange': 'valve_api',
            'routing_key': 'valve_api_call'
        },
        'matches.management.tasks.CycleApiCall': {
            'exchange': 'rpr',
            'routing_key': 'rpr'
        },
        'items.management.tasks.MirrorItemSchema': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'items.management.tasks.UpdateItemSchema': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'matches.management.tasks.UpdateMatch': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'players.management.tasks.UpdateClientPersonas':
        {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'players.management.tasks.MirrorClientPersonas': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'players.management.tasks.MirrorClientMatches': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'players.management.tasks.MirrorPlayerData': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'heroes.management.tasks.MirrorHeroSkillData': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'matches.management.tasks.MirrorMatches': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'teams.management.tasks.MirrorTeams': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'teams.management.tasks.UpdateTeam': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'teams.management.tasks.MirrorTeamDetails': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'teams.management.tasks.UpdateTeamLogos': {
            'exchange': 'valve_api',
            'routing_key': 'valve_api_call'
        },
        'leagues.management.tasks.MirrorLeagues': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'leagues.management.tasks.UpdateLeagueGames': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'leagues.management.tasks.CreateLeagues': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'leagues.management.tasks.UpdateLeagueGames': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'leagues.management.tasks.MirrorLeagueLogos': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'leagues.management.tasks.UpdateLeagueLogos': {
            'exchange': 'valve_api',
            'routing_key': 'valve_api_call'
        },
        'leagues.management.tasks.MirrorLeagueSchedule': {
            'exchange': 'valve_api',
            'routing_key': 'valve_api_call'
        },
        'leagues.management.tasks.UpdateLeagueSchedule': {
            'exchange': 'valve_api',
            'routing_key': 'valve_api_call'
        },
        'players.management.tasks.MirrorProNames': {
            'exchange': 'management',
            'routing_key': 'management'
        },
        'players.management.tasks.UpdateProNames': {
            'exchange': 'db',
            'routing_key': 'db'
        },

    }

    CELERY_DEFAULT_EXCHANGE = 'default'
    CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
    CELERY_DEFAULT_ROUTING_KEY = 'default'
    CELERY_DEFAULT_QUEUE = 'default'

    TASK_MAX_RETRIES = 6  # Note: This is a custom var.

    CELERY_ANNOTATIONS = {
        "datadrivendota.management.tasks.ValveApiCall": {
            "rate_limit": VALVE_RATE,
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'items.management.tasks.UpdateItemSchema': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'items.management.tasks.MirrorItemSchema': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'matches.management.tasks.CycleApiCall': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'matches.management.tasks.UpdateMatch.': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'players.management.tasks.UpdateClientPersonas':
        {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'players.management.tasks.MirrorClientPersonas': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'players.management.tasks.MirrorClientMatches': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'players.management.tasks.MirrorPlayerData': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'heroes.management.tasks.MirrorHeroSkillData': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'matches.management.tasks.MirrorMatches': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'teams.management.tasks.MirrorTeams': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'teams.management.tasks.MirrorTeamDetails': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'teams.management.tasks.UpdateTeam': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'teams.management.tasks.UpdateTeamLogos': {
            "rate_limit": VALVE_RATE,
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.MirrorLeagues': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.UpdateLeagueGames': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.CreateLeagues': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.UpdateLeagueGames': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.MirrorLeagueLogos': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.UpdateLeagueLogos': {
            "rate_limit": VALVE_RATE,
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.UpdateLeagueSchedule': {
            "rate_limit": VALVE_RATE,
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.MirrorLeagueSchedule': {
            "rate_limit": VALVE_RATE,
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'players.management.tasks.MirrorProNames': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'players.management.tasks.UpdateProNames': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },

    }

    CELERYBEAT_SCHEDULE = {
        'reflect-item-schema-hourly': {
            'task': 'items.management.tasks.MirrorItemSchema',
            'schedule': timedelta(hours=1),
        },
        'reflect-league-schedule-hourly': {
            'task': 'leagues.management.tasks.MirrorLeagueSchedule',
            'schedule': timedelta(hours=1),
        },
        'reflect-league-schedule-hourly': {
            'task': 'leagues.management.tasks.MirrorLiveGames',
            'schedule': timedelta(seconds=10),
        },
    }

app.config_from_object(Config)

if __name__ == '__main__':
    app.start()
