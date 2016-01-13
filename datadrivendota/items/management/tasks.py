import json
import requests
from steam import vdf
from django.conf import settings
from celery import Task, chain
from datadrivendota.redis_app import redis_app as redis
from datadrivendota.management.tasks import (
    ValveApiCall,
    ApiContext,
    ApiFollower
)
import logging

logger = logging.getLogger(__name__)


class MirrorItemSchema(Task):
    """
    Pings for live game vdf, passes to updater
    """

    def run(self):
        logger.info("Pinging the live league json")
        c = ApiContext()
        vac = ValveApiCall()
        uis = UpdateItemSchema()
        c = chain(
            vac.s(api_context=c, mode='GetSchemaURL'),
            uis.s()
        )
        c.delay()


class UpdateItemSchema(ApiFollower):
    """
    Sets the redis store of the item json after parsing from vdf
    """
    def run(self, api_context, json_data, response_code, url):

        url = json_data['result']['items_game_url']

        logger.info("Item schema url: {0}".format(url))
        response = requests.get(url)
        logger.info("Got item schema")
        data = vdf.loads(response.text)
        logger.info("Item schema made json")
        raw_data = self.strip_wrapper(data)
        logger.info("Item schema stripped")
        trimmed_data = self.get_leagues(raw_data)
        logger.info("Item schema refactored")

        logger.info("Setting item schema in redis (url: {0})".format(url))
        redis.set(settings.ITEM_SCHEMA_KEY, json.dumps(trimmed_data))
        logger.info("Item schema set in redis (url: {0})".format(url))

    def strip_wrapper(self, json_data):
        return json_data['items_game']['items']

    def get_leagues(self, json_data):
        return_dct = {}
        for key, val in json_data.iteritems():
            if (
                val.get('prefab', None) == 'league' and
                val.get('tool', {}).get('usage', {}).get('league_id', None)
                    is not None
               ):
                    league_id = int(val['tool']['usage']['league_id'])
                    return_dct[league_id] = val
                    return_dct[league_id]['itemdef'] = key
        return return_dct
