import os
import json
file_location = os.path.dirname(__file__)

with open(file_location+'/heroes.json', 'r') as f:
    heroes = json.loads(f.read())

with open(file_location+'/ability_text.json', 'r') as f:
    ability_text = json.loads(f.read())

with open(file_location+'/ability_numbers.json', 'r') as f:
    ability_numbers = json.loads(f.read())

with open(file_location+'/ability_merge.json', 'r') as f:
    ability_merge = json.loads(f.read())
