import json
from redis import StrictRedis
from os import getenv
from django.conf import settings

redis_app = StrictRedis().from_url(getenv('REDISTOGO_URL'))


def load_games():
    redis = redis_app
    return json.loads(redis.get(settings.LIVE_JSON_KEY))['games']


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
