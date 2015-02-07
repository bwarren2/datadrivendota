from redis import StrictRedis
from os import getenv

redis_app = StrictRedis().from_url(getenv('REDISTOGO_URL'))
