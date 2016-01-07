import json
import os
file_location = os.path.dirname(__file__)


with open(file_location+'/valid_match.json', 'r') as f:
    valid_match = json.loads(f.read())

with open(file_location+'/not_found_match.json', 'r') as f:
    not_found_match = json.loads(f.read())

with open(file_location+'/empty_match.json', 'r') as f:
    empty_match = json.loads(f.read())
