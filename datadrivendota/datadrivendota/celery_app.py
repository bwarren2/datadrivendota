from __future__ import absolute_import
from os import getenv
from kombu import Exchange, Queue
from django.conf import settings
from datetime import timedelta
from celery import Celery

app = Celery('datadrivendota')


def inferred_annotations(tsk):
    defaults = {
        'acks_late': True,
        'max_retries': 7,
        'trail': False,
        'default_retry_delay': 600,
    }
    tsk_annotations = tsk.get('annotations', {})
    if 'standalone' in tsk_annotations.keys():
        return tsk_annotations
    else:
        defaults.update(tsk)
        return defaults


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

    CELERY_DEFAULT_EXCHANGE = 'default'
    CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
    CELERY_DEFAULT_ROUTING_KEY = 'default'
    CELERY_DEFAULT_QUEUE = 'default'

    # List of modules to import when celery starts.
    CELERY_IMPORTS = (
        "matches.management.tasks",
        "items.management.tasks",
        "heroes.management.tasks",
        "players.management.tasks",
        "teams.management.tasks",
        "parserpipe.management.tasks",
        "datadrivendota.management.tasks",
        # Importing from the module causes name conflicts in the scheduler
        "leagues.management.tasks.league",
        "leagues.management.tasks.league_schedule",
        "leagues.management.tasks.live_game",
    )

    # What happens if we do not use redis?.
    CELERY_RESULT_BACKEND = getenv('REDISTOGO_URL')+'?new_join=1'

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
        Queue(
            'parsing',
            Exchange('parsing'),
            routing_key='parsing'
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
        # This handles the callbacks of the java parser.  Unknown speed.

    )
    TASKS = {
        'parserpipe.management.tasks.CreateMatchParse': {
            'routes': {
                'exchange': 'parsing',
                'routing_key': 'parsing'
            },
            'annotations': {
                'max_retries': 0,
            }
        },
        'parserpipe.management.tasks.KickoffMatchRequests': {
            'routes': {
                'exchange': 'parsing',
                'routing_key': 'parsing'
            },
            'annotations': {
                'max_retries': 0,
            }
        },
        'parserpipe.management.tasks.MergeMatchRequestReplay': {
            'routes': {
                'exchange': 'parsing',
                'routing_key': 'parsing'
            },
            'annotations': {
                'max_retries': 0,
            }
        },
        'parserpipe.management.tasks.ReadParseResults': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            },
            'annotations': {
                'max_retries': 0,
            }
        },
        'parserpipe.management.tasks.UpdatePmsReplays': {
            'routes': {
                'exchange': 'parsing',
                'routing_key': 'parsing'
            },
            'annotations': {
                "time_limit": 240,
                "soft_time_limit": 235,
            }
        },
        'parserpipe.management.tasks.UpdateParseEnd': {
            'routes': {
                'exchange': 'parsing',
                'routing_key': 'parsing'
            },
            'annotations': {
                "time_limit": 240,
                "soft_time_limit": 235,
            }
        },
        'datadrivendota.management.tasks.ValveApiCall': {
            'routes': {
                'exchange': 'valve_api',
                'routing_key': 'valve_api_call'
            },
            'annotations': {
                "rate_limit": VALVE_RATE,
            }
        },
        'heroes.management.tasks.CheckHeroIntegrity': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'heroes.management.tasks.MirrorHeroSkillData': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'items.management.tasks.MirrorItemSchema': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'items.management.tasks.UpdateItemSchema': {
            'routes': {
                'exchange': 'db',
                'routing_key': 'db'
            }
        },
        'leagues.management.tasks.league_schedule.MirrorLeagueSchedule': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            },
            'annotations': {
                "rate_limit": VALVE_RATE,
            }
        },
        'leagues.management.tasks.live_game.MirrorLiveGames': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            },
            'annotations': {
                'max_retries': 0,
            }
        },
        'leagues.management.tasks.league.MirrorRecentLeagues': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'leagues.management.tasks.league.UpdateLeagueLogo': {
            'routes': {
                'exchange': 'valve_api',
                'routing_key': 'valve_api_call'
            },
            'annotations': {
                "rate_limit": VALVE_RATE,
            }
        },
        'leagues.management.tasks.league_schedule.UpdateLeagueSchedule': {
            'routes': {
                'exchange': 'db',
                'routing_key': 'db'
            },
            'annotations': {
                "rate_limit": VALVE_RATE,
            }
        },
        'leagues.management.tasks.live_game.UpdateLiveMatches': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            },
        },
        'matches.management.tasks.CheckMatchIntegrity': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'matches.management.tasks.CycleApiCall': {
            'routes': {
                'exchange': 'rpr',
                'routing_key': 'rpr'
            }
        },
        'matches.management.tasks.MirrorRecentMatches': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'matches.management.tasks.MirrorMatches': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'matches.management.tasks.UpdateMatch': {
            'routes': {
                'exchange': 'db',
                'routing_key': 'db'
            }
        },
        'matches.management.tasks.UpdateMatchValidity': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'players.management.tasks.MirrorClientMatches': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'players.management.tasks.MirrorClientPersonas': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'players.management.tasks.MirrorPlayerData': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'players.management.tasks.MirrorProNames': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'players.management.tasks.UpdateClientPersonas': {
            'routes': {
                'exchange': 'db',
                'routing_key': 'db'
            }
        },
        'players.management.tasks.UpdateProNames': {
            'routes': {
                'exchange': 'db',
                'routing_key': 'db'
            }
        },
        'teams.management.tasks.MirrorRecentTeams': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'teams.management.tasks.MirrorTeamDetails': {
            'routes': {
                'exchange': 'integrity',
                'routing_key': 'integrity'
            }
        },
        'teams.management.tasks.UpdateTeam': {
            'routes': {
                'exchange': 'db',
                'routing_key': 'db'
            }
        },
        'teams.management.tasks.UpdateTeamLogo': {
            'routes': {
                'exchange': 'db',
                'routing_key': 'db'
            },
            'annotations': {
                "rate_limit": VALVE_RATE,
            }
        }
    }

    CELERY_ANNOTATIONS = {
        x: inferred_annotations(y) for x, y in TASKS.iteritems()
    }

    CELERY_ROUTES = {x: y['routes'] for x, y in TASKS.iteritems()}

    CELERYBEAT_SCHEDULE = {
        # Weekly
        'reflect-pro-names-weekly': {
            'task': 'players.management.tasks.MirrorProNames',
            'schedule': timedelta(weeks=1),
        },
        # Daily
        'check-hero-integrity-daily': {
            'task': 'heroes.management.tasks.CheckHeroIntegrity',
            'schedule': timedelta(days=1),
        },
        'reflect-league-schedule-daily': {
            'task': (
                'leagues.management.tasks.league_schedule.'
                'MirrorLeagueSchedule'
                ),
            'schedule': timedelta(days=1),
        },
        'reflect-item-schema-daily': {
            'task': 'items.management.tasks.MirrorItemSchema',
            'schedule': timedelta(days=1),
        },
        'reflect-recent-teams-daily': {
            'task': 'teams.management.tasks.MirrorRecentTeams',
            'schedule': timedelta(days=1),
        },
        'reflect-recent-leagues-daily': {
            'task': 'leagues.management.tasks.league.MirrorRecentLeagues',
            'schedule': timedelta(days=1),
        },
        # Fast
        'check-match-integrity-hourly': {
            'task': 'matches.management.tasks.CheckMatchIntegrity',
            'schedule': timedelta(hours=1),
        },
        'reflect-recent-matches-hourly': {
            'task': 'matches.management.tasks.MirrorRecentMatches',
            'schedule': timedelta(minutes=30),
        },
        'check-match-validity-fast': {
            'task': 'matches.management.tasks.UpdateMatchValidity',
            'schedule': timedelta(minutes=30),
        },
        'reflect-clients-fast': {
            'task': 'players.management.tasks.MirrorClientMatches',
            'schedule': timedelta(minutes=15),
        },
        'check-parse-result-fast': {
            'task': 'parserpipe.management.tasks.ReadParseResults',
            'schedule': timedelta(minutes=10),
        },
        'reflect-live-games-fast': {
            'task': 'leagues.management.tasks.live_game.MirrorLiveGames',
            'schedule': timedelta(minutes=5),
        },
    }

app.config_from_object(Config)

if __name__ == '__main__':
    app.start()
