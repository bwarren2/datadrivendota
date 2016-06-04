import json
import os
file_location = os.path.dirname(__file__)


with open(file_location+'/all_income.json', 'r') as f:
    all_income = json.loads(f.read())

with open(file_location+'/bot_match_details.json', 'r') as f:
    bot_match_details = json.loads(f.read())
