# -*- coding: utf-8 -*- i
import os
import json
file_location = os.path.dirname(__file__)
schedule_strng = u"""
{
    "result": {
        "games": [
            {
                "league_id": 2472,
                "game_id": 1,
                "teams": [
                    {
                        "team_id": 1946671,
                        "team_name": "NON Servium",
                        "logo": 0
                    },
                    {
                        "team_id": 1599193,
                        "team_name": "Tap Face",
                        "logo": 774929666700592453
                    }
                ]
                ,
                "starttime": 1423686600,
                "comment": "",
                "final": false
            },
            {
                "league_id": 2377,
                "game_id": 18,
                "teams": [
                    {
                        "team_id": 1905619,
                        "team_name": "Wheel Whreck While Whistling",
                        "logo": 539627912847820521
                    },
                    {
                        "team_id": 1321909,
                        "team_name": "Isurus Gaming HyperX",
                        "logo": 794060367828459932
                    }
                ]
                ,
                "starttime": 1423701000,
                "comment": "Dota 2 Canada Cup Season 4 - Group B Day 1. Isurus vs Wheel Wreck While Whistling",
                "final": false
            }
        ]
    }
}
"""
good_league_schedule = json.loads(schedule_strng)


# Live games test samples
with open(file_location+'/live_games.json', 'r') as f:
    data = f.read()
good_live_games = json.loads(data)

with open(file_location+'/clean_url_data.json', 'r') as f:
    data = f.read()
live_clean_url_json = json.loads(data)

with open(file_location+'/live_get_players.json', 'r') as f:
    data = f.read()
live_get_players = json.loads(data)

with open(file_location+'/live_game_data.json', 'r') as f:
    data = f.read()
live_game_data = json.loads(data)

with open(file_location+'/live_side_data.json', 'r') as f:
    data = f.read()
live_side_data = json.loads(data)

with open(file_location+'/live_pickbans.json', 'r') as f:
    data = f.read()
live_pickbans = json.loads(data)

with open(file_location+'/live_merge_logos.json', 'r') as f:
    data = f.read()
live_merge_logos = json.loads(data)

with open(file_location+'/live_states.json', 'r') as f:
    data = f.read()
live_states = json.loads(data)
