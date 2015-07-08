from __future__ import absolute_import
from os import getenv
from kombu import Exchange, Queue
from django.conf import settings
from datetime import timedelta
from celery import Celery

app = Celery('datadrivendota')


class Config(object):
    BROKER_POOL_LIMIT = int(getenv('BROKER_POOL_LIMIT', 1))
    BROKER_URL = settings.BROKER_URL
    BROKER_CONNECTION_TIMEOUT = int(getenv('BROKER_CONNECTION_TIMEOUT'))
    BROKER_CONNECTION_RETRY = True
    CELERYD_CONCURRENCY = int(getenv('CELERYD_CONCURRENCY'))

    # Note: Pickle is a security concern in celery.
    # But, when we are passing around API context objects,
    # it is the only one that works.
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
    CELERY_TASK_SERIALIZER = 'pickle'
    CELERY_RESULT_SERIALIZER = 'pickle'

    # List of modules to import when celery starts.
    CELERY_IMPORTS = (
        "matches.management.tasks",
        "matches.management.parser_tasks",
        "items.management.tasks",
        "heroes.management.tasks",
        "players.management.tasks",
        "leagues.management.tasks",
        "teams.management.tasks",
        "accounts.management.tasks",
        "datadrivendota.management.tasks",
    )

    # What happens if we do not use redis?.
    CELERY_RESULT_BACKEND = getenv('REDISTOGO_URL')

    # What happens if we do not use redis?.
    CELERY_TIMEZONE = settings.TIME_ZONE

    # Stop a bazillion fake queues from being made with results.  Time in sec.
    CELERY_TASK_RESULT_EXPIRES = int(getenv('RESULT_EXPIRY_RATE'))

    # Only store errors.
    # NOTE: this means that you cannot get the results of the tasks.
    CELERY_IGNORE_RESULT = getenv('CELERY_IGNORE_RESULT') == 'True'
    CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

    CELERYD_TASK_TIME_LIMIT = int(getenv('CELERYD_TASK_TIME_LIMIT'))
    CELERY_ACKS_LATE = True

    # Experimenting
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

    # Where celery emails from.
    SERVER_EMAIL = "celery@datadrivendota.com"

    CELERY_QUEUES = (
        # This is a fast queue for tasks that check data integrity.
        # It should never back up.
        Queue(
            'integrity',
            Exchange('integrity'),
            routing_key='integrity'
        ),
        # This is a slower queue for tasks that hit Valve's API.
        # We would love this to be fast and never back up,
        # but rate limiting gets in the way.
        Queue(
            'api_call',
            Exchange('valve_api'),
            routing_key='valve_api_call'
        ),
        # This is a slower queue for tasks that hit our database or redis.
        # Scaling to keep this moving quickly is allowed, based on conn caps.
        Queue(
            'db_upload',
            Exchange('db'),
            routing_key='db'
        ),
        # This is a slower queue for tasks that cycle through api calls.
        # It is rate limited by valve's rate, and is broken out for clarity.
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
            'exchange': 'integrity',
            'routing_key': 'integrity'
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
            'exchange': 'db',
            'routing_key': 'db'
        },
        'players.management.tasks.MirrorClientPersonas': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'players.management.tasks.MirrorClientMatches': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'players.management.tasks.MirrorPlayerData': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'heroes.management.tasks.MirrorHeroSkillData': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'heroes.management.tasks.CheckHeroIntegrity': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'matches.management.tasks.MirrorMatches': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'matches.management.tasks.UpdateMatchValidity': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'matches.management.tasks.CheckMatchIntegrity': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'teams.management.tasks.MirrorRecentTeams': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'leagues.management.tasks.MirrorLiveGames': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'teams.management.tasks.UpdateTeam': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'teams.management.tasks.MirrorTeamDetails': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'teams.management.tasks.UpdateTeamLogo': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'leagues.management.tasks.MirrorRecentLeagues': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'leagues.management.tasks.CreateLeagues': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'leagues.management.tasks.MirrorLeagues': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'leagues.management.tasks.UpdateLeagueLogos': {
            'exchange': 'valve_api',
            'routing_key': 'valve_api_call'
        },
        'leagues.management.tasks.MirrorLeagueSchedule': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
        },
        'leagues.management.tasks.UpdateLeagueSchedule': {
            'exchange': 'db',
            'routing_key': 'db'
        },
        'players.management.tasks.MirrorProNames': {
            'exchange': 'integrity',
            'routing_key': 'integrity'
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
        'matches.management.tasks.UpdateMatch': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'matches.management.tasks.UpdateMatchValidity': {
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
        'heroes.management.tasks.CheckHeroIntegrity': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'matches.management.tasks.MirrorMatches': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'matches.management.tasks.CheckMatchIntegrity': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'teams.management.tasks.MirrorRecentTeams': {
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
        'teams.management.tasks.UpdateTeamLogo': {
            "rate_limit": VALVE_RATE,
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.MirrorRecentLeagues': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.CreateLeagues': {
            'acks_late': True,
            'max_retries': TASK_MAX_RETRIES,
            'trail': False,
        },
        'leagues.management.tasks.MirrorLeagues': {
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
        'leagues.management.tasks.MirrorLiveGames': {
            'acks_late': True,
            'max_retries': 0,
            'trail': False,
        },

    }

    CELERYBEAT_SCHEDULE = {
        # Weekly
        'reflect-pro-names-weekly': {
            'task': 'players.management.tasks.MirrorProNames',
            'schedule': timedelta(weeks=1),
        },
        'reflect-hero-skill-weekly': {
            'task': 'heroes.management.tasks.MirrorHeroSkillData',
            'schedule': timedelta(weeks=1),
        },
        'reflect-leagues-daily': {
            'task': 'leagues.management.tasks.MirrorLeagues',
            'schedule': timedelta(weeks=1),
        },
        # Daily
        'check-hero-integrity-daily': {
            'task': 'heroes.management.tasks.CheckHeroIntegrity',
            'schedule': timedelta(days=1),
        },
        'check-match-integrity-daily': {
            'task': 'matches.management.tasks.CheckMatchIntegrity',
            'schedule': timedelta(days=1),
        },
        'check-match-validity-daily': {
            'task': 'matches.management.tasks.UpdateMatchValidity',
            'schedule': timedelta(days=1),
        },
        'reflect-league-schedule-daily': {
            'task': 'leagues.management.tasks.MirrorLeagueSchedule',
            'schedule': timedelta(days=1),
        },
        'reflect-client-persona-daily': {
            'task': 'players.management.tasks.MirrorClientPersonas',
            'schedule': timedelta(days=1),
        },
        # Hourly
        'reflect-item-schema-hourly': {
            'task': 'items.management.tasks.MirrorItemSchema',
            'schedule': timedelta(hours=1),
        },
        'reflect-client-matches-hourly': {
            'task': 'players.management.tasks.MirrorClientMatches',
            'schedule': timedelta(hours=1),
        },
        # Fast
        # 'reflect-recent-leagues-daily': {
        #     'task': 'leagues.management.tasks.MirrorRecentLeagues',
        #     'schedule': timedelta(minutes=1),
        # },
        # 'reflect-recent-teams-daily': {
        #     'task': 'teams.management.tasks.MirrorRecentTeams',
        #     'schedule': timedelta(minutes=1),
        # },
        # 'reflect-live-games-fast': {
        #     'task': 'leagues.management.tasks.MirrorLiveGames',
        #     'schedule': timedelta(seconds=10),
        # },
    }

app.config_from_object(Config)

if __name__ == '__main__':
    app.start()
