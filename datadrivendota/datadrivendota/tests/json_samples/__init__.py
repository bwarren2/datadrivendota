import json
import os
file_location = os.path.dirname(__file__)


with open(file_location+'/valid_match.json', 'r') as f:
    valid_match = json.loads(f.read())

with open(file_location+'/broken_ugc.json', 'r') as f:
    broken_ugc = json.loads(f.read())
