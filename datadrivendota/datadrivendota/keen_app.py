import keen
from os import getenv

keen.project_id = getenv('KEEN_PROJECT_ID')
keen.write_key = getenv('KEEN_WRITE_KEY')
keen.read_key = getenv('KEEN_READ_KEY')
keen_client = keen
