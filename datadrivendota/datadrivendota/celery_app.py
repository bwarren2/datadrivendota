from __future__ import absolute_import
from os import getenv
from kombu import Exchange, Queue


from celery import Celery

app = Celery('datadrivendota')


#app.config_from_object('celery_config')

class Config:
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

    SERVER_EMAIL = "celery@datadrivendota.com"


    CELERY_QUEUES = (
        Queue('management', Exchange('management'), routing_key='management'),
        Queue('api_call',  Exchange('valve_api'),   routing_key='valve_api_call'),
        Queue('db_upload',  Exchange('db'),   routing_key='db'),
        Queue('rpr',  Exchange('rpr'),   routing_key='rpr'),
    )

    CELERY_ROUTES = {
        'matches.management.tasks.valve_api_calls.ValveApiCall': {'exchange': 'valve_api','routing_key':'valve_api_call'},
        'matches.management.tasks.valve_api_calls.RetrievePlayerRecords': {'exchange': 'rpr','routing_key':'rpr'},
        'matches.management.tasks.valve_api_calls.UploadMatch': {'exchange': 'db','routing_key':'db'},
        'matches.management.tasks.valve_api_calls.RefreshUpdatePlayerPersonas': {'exchange': 'management', 'routing_key':'management'},
        'matches.management.tasks.valve_api_calls.UpdatePlayerPersonas': {'exchange': 'db','routing_key':'db'},
        'matches.management.tasks.valve_api_calls.RefreshPlayerMatchDetail': {'exchange': 'management','routing_key':'management'},
        'matches.management.tasks.valve_api_calls.AcquirePlayerData': {'exchange': 'management','routing_key':'management'},
        'matches.management.tasks.valve_api_calls.AcquireHeroSkillData': {'exchange': 'management','routing_key':'management'},

    }

    CELERY_DEFAULT_EXCHANGE = 'default'
    CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
    CELERY_DEFAULT_ROUTING_KEY = 'default'
    CELERY_DEFAULT_QUEUE = 'default'

    CELERY_ANNOTATIONS = {
        "matches.management.tasks.valve_api_calls.ValveApiCall": {"rate_limit": VALVE_RATE,
                                                                  'acks_late': True,
                                                                  'max_retries':5},
        'matches.management.tasks.valve_api_calls.RetrievePlayerRecords': {'acks_late': True,'max_retries':5, },
        'matches.management.tasks.valve_api_calls.UploadMatch': {'acks_late': True,'max_retries':5, },
        'matches.management.tasks.valve_api_calls.RefreshUpdatePlayerPersonas': {'acks_late': True,'max_retries':5,},
        'matches.management.tasks.valve_api_calls.UpdatePlayerPersonas': {'acks_late': True,'max_retries':5, },
        'matches.management.tasks.valve_api_calls.RefreshPlayerMatchDetail': {'acks_late': True,'max_retries':5,},
        'matches.management.tasks.valve_api_calls.AcquirePlayerData': {'acks_late': True,'max_retries':5, },
        'matches.management.tasks.valve_api_calls.AcquireHeroSkillData': {'acks_late': True,'max_retries':5, },

    }



app.config_from_object(Config)

if __name__ == '__main__':
    app.start()

