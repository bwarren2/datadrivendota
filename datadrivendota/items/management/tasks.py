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
    def run(self, urldata):
        url = urldata['result']['items_game_url']
        response = requests.get(url)
        data = vdf.loads(response.text)
        json_data = json.dumps(data)
        redis.set(settings.ITEM_SCHEMA_KEY, json_data)