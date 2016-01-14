import json
from django.conf import settings
from datadrivendota.redis_app import redis_app as redis


def get_league_schema():
    data = json.loads(redis.get(settings.ITEM_SCHEMA_KEY))
    # Int indices implicitly get cast to str in storage
    data = {int(x): y for x, y in data.iteritems()}
    return data
