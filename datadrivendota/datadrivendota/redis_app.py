import json
from redis import StrictRedis
from os import getenv
from django.conf import settings

redis_app = StrictRedis(
    socket_timeout=settings.REDIS_TIMEOUT
).from_url(getenv('REDISTOGO_URL'))


def get_games():
    return json.loads(redis_app.get(settings.LIVE_JSON_KEY))


def set_games(data):
    return redis_app.set(settings.LIVE_JSON_KEY, json.dumps(data))


def timeline_key(match_id):
    return "{0}_{1}_timeline".format(
        settings.LIVE_JSON_KEY,
        match_id
    )


def slice_key(match_id):
    return "{0}_{1}_slice".format(
        settings.LIVE_JSON_KEY,
        match_id
    )
