import json
from django.conf import settings
from datadrivendota.redis_app import redis_app as redis


def get_item_schema():
    data = json.loads(redis.get(settings.ITEM_SCHEMA_KEY))
    return data['items_game']['items']


def get_league_schema():
    data = get_item_schema()
    return_dct = {}
    for key, val in data.iteritems():
        if (
            'prefab' in val.keys() and val['prefab'] == 'league'
            and 'league_id' in val['tool']['usage'].keys()
        ):
            league_id = int(val['tool']['usage']['league_id'])
            return_dct[league_id] = val
            return_dct[league_id]['itemdef'] = key
    return return_dct
