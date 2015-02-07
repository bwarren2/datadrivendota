# -*- coding: utf-8 -*- i

import json

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

live_strng = u"""{

    "result":

{

    "games":

[

{

    "players":

[

{

    "account_id": 53513899,
    "name": "[Urge]",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 40712831,
    "name": "Ѵiewtiful Joe™",
    "hero_id": 110,
    "team": 1

},
{

    "account_id": 65277332,
    "name": "CircleSmithy",
    "hero_id": 104,
    "team": 0

},
{

    "account_id": 81442707,
    "name": "No Country for Dank Memes",
    "hero_id": 63,
    "team": 1

},
{

    "account_id": 42989425,
    "name": "Simi510",
    "hero_id": 9,
    "team": 0

},
{

    "account_id": 51526675,
    "name": "Nintony",
    "hero_id": 95,
    "team": 0

},
{

    "account_id": 20447939,
    "name": "Grantrithor",
    "hero_id": 18,
    "team": 1

},
{

    "account_id": 22011014,
    "name": "BROCCOLI",
    "hero_id": 83,
    "team": 1

},
{

    "account_id": 107879270,
    "name": "S A D O G R E 2 0 0 1",
    "hero_id": 21,
    "team": 0

},
{

    "account_id": 27414945,
    "name": "Dec",
    "hero_id": 25,
    "team": 1

},
{

    "account_id": 106451882,
    "name": "MadAT3Z",
    "hero_id": 45,
    "team": 0

},

    {
        "account_id": 181829645,
        "name": "Lobby: 1/1 Waifubot",
        "hero_id": 0,
        "team": 2
    }

],
"radiant_team":
{

    "team_name": "^^ My Waifu ^^",
    "team_id": 900238,
    "team_logo": 0,
    "complete": false

},
"lobby_id": 23904643247648064,
"match_id": 1272220008,
"spectators": 0,
"league_id": 1645,
"stream_delay_s": 10,
"radiant_series_wins": 0,
"dire_series_wins": 0,
"series_type": 0,
"league_tier": 0,
"scoreboard":
{

    "duration": 1067.5059814453125,
    "roshan_respawn_timer": 0,
    "radiant":

{

    "score": 14,
    "tower_state": 1983,
    "barracks_state": 63,
    "players":

[

{

    "player_slot": 1,
    "account_id": 65277332,
    "hero_id": 104,
    "kills": 1,
    "death": 4,
    "assists": 2,
    "last_hits": 37,
    "denies": 0,
    "gold": 70,
    "level": 8,
    "gold_per_min": 238,
    "xp_per_min": 233,
    "ultimate_state": 1,
    "ultimate_cooldown": 8,
    "item0": 1,
    "item1": 11,
    "item2": 182,
    "item3": 29,
    "item4": 0,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": -7296,
    "position_y": -6592,
    "net_worth": 3795

},
{

    "player_slot": 2,
    "account_id": 42989425,
    "hero_id": 9,
    "kills": 1,
    "death": 3,
    "assists": 2,
    "last_hits": 27,
    "denies": 4,
    "gold": 826,
    "level": 11,
    "gold_per_min": 211,
    "xp_per_min": 403,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 40,
    "item1": 0,
    "item2": 36,
    "item3": 41,
    "item4": 29,
    "item5": 0,
    "respawn_timer": 30,
    "position_x": -2718.310791015625,
    "position_y": -617.0977172851562,
    "net_worth": 2656

},
{

    "player_slot": 3,
    "account_id": 51526675,
    "hero_id": 95,
    "kills": 9,
    "death": 0,
    "assists": 3,
    "last_hits": 108,
    "denies": 0,
    "gold": 1583,
    "level": 13,
    "gold_per_min": 547,
    "xp_per_min": 526,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 36,
    "item1": 185,
    "item2": 212,
    "item3": 50,
    "item4": 172,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": -2229.586181640625,
    "position_y": 637.3580322265625,
    "net_worth": 9943

},
{

    "player_slot": 4,
    "account_id": 107879270,
    "hero_id": 21,
    "kills": 1,
    "death": 1,
    "assists": 3,
    "last_hits": 67,
    "denies": 7,
    "gold": 560,
    "level": 11,
    "gold_per_min": 321,
    "xp_per_min": 443,
    "ultimate_state": 1,
    "ultimate_cooldown": 30,
    "item0": 34,
    "item1": 102,
    "item2": 50,
    "item3": 46,
    "item4": 25,
    "item5": 165,
    "respawn_timer": 33,
    "position_x": -1279.8599853515625,
    "position_y": 3012.80712890625,
    "net_worth": 5660

},

    {
        "player_slot": 5,
        "account_id": 106451882,
        "hero_id": 45,
        "kills": 2,
        "death": 3,
        "assists": 5,
        "last_hits": 13,
        "denies": 4,
        "gold": 877,
        "level": 10,
        "gold_per_min": 212,
        "xp_per_min": 328,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 73,
        "item1": 180,
        "item2": 46,
        "item3": 42,
        "item4": 0,
        "item5": 0,
        "respawn_timer": 14,
        "position_x": -726.6279296875,
        "position_y": -420.1440734863281,
        "net_worth": 3102
    }

],
"abilities":
[

{

    "ability_id": 5186,
    "ability_level": 4

},
{

    "ability_id": 5187,
    "ability_level": 3

},
{

    "ability_id": 5188,
    "ability_level": 2

},

        {
            "ability_id": 5189,
            "ability_level": 1
        }
    ]

},
"dire":
{

    "score": 11,
    "tower_state": 2046,
    "barracks_state": 63,
    "players":

[

{

    "player_slot": 1,
    "account_id": 40712831,
    "hero_id": 110,
    "kills": 0,
    "death": 6,
    "assists": 3,
    "last_hits": 26,
    "denies": 10,
    "gold": 882,
    "level": 9,
    "gold_per_min": 183,
    "xp_per_min": 277,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 214,
    "item1": 16,
    "item2": 16,
    "item3": 0,
    "item4": 0,
    "item5": 0,
    "respawn_timer": 27,
    "position_x": 505.53179931640625,
    "position_y": 2972.796875,
    "net_worth": 1982

},
{

    "player_slot": 2,
    "account_id": 81442707,
    "hero_id": 63,
    "kills": 3,
    "death": 2,
    "assists": 4,
    "last_hits": 61,
    "denies": 3,
    "gold": 645,
    "level": 11,
    "gold_per_min": 353,
    "xp_per_min": 417,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 24,
    "item1": 212,
    "item2": 29,
    "item3": 16,
    "item4": 69,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": -2106.819091796875,
    "position_y": 735.283447265625,
    "net_worth": 6005

},
{

    "player_slot": 3,
    "account_id": 20447939,
    "hero_id": 18,
    "kills": 1,
    "death": 3,
    "assists": 3,
    "last_hits": 11,
    "denies": 11,
    "gold": 198,
    "level": 8,
    "gold_per_min": 174,
    "xp_per_min": 214,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 0,
    "item1": 17,
    "item2": 36,
    "item3": 73,
    "item4": 0,
    "item5": 29,
    "respawn_timer": 0,
    "position_x": 246.5702667236328,
    "position_y": 248.07403564453125,
    "net_worth": 2123

},
{

    "player_slot": 4,
    "account_id": 22011014,
    "hero_id": 83,
    "kills": 2,
    "death": 0,
    "assists": 2,
    "last_hits": 23,
    "denies": 1,
    "gold": 981,
    "level": 9,
    "gold_per_min": 226,
    "xp_per_min": 303,
    "ultimate_state": 1,
    "ultimate_cooldown": 36,
    "item0": 46,
    "item1": 0,
    "item2": 36,
    "item3": 92,
    "item4": 0,
    "item5": 180,
    "respawn_timer": 0,
    "position_x": -1884.623291015625,
    "position_y": 1113.0892333984375,
    "net_worth": 3906

},

    {
        "player_slot": 5,
        "account_id": 27414945,
        "hero_id": 25,
        "kills": 5,
        "death": 3,
        "assists": 2,
        "last_hits": 40,
        "denies": 4,
        "gold": 1359,
        "level": 11,
        "gold_per_min": 327,
        "xp_per_min": 410,
        "ultimate_state": 1,
        "ultimate_cooldown": 31,
        "item0": 63,
        "item1": 185,
        "item2": 46,
        "item3": 42,
        "item4": 43,
        "item5": 0,
        "respawn_timer": 32,
        "position_x": -181.20437622070312,
        "position_y": 2406.783935546875,
        "net_worth": 5059
    }

],
"abilities":
[

{

    "ability_id": 5040,
    "ability_level": 4

},
{

    "ability_id": 5041,
    "ability_level": 4

},
{

    "ability_id": 5042,
    "ability_level": 2

},

                {
                    "ability_id": 5043,
                    "ability_level": 1
                }
            ]
        }
    }

},
{

    "players":

[

{

    "account_id": 102588710,
    "name": "Filo",
    "hero_id": 90,
    "team": 0

},
{

    "account_id": 97490608,
    "name": "CrackPants",
    "hero_id": 71,
    "team": 0

},
{

    "account_id": 207414944,
    "name": "I hate everyone",
    "hero_id": 0,
    "team": 4

},
{

    "account_id": 69256187,
    "name": "04fan1997",
    "hero_id": 95,
    "team": 1

},
{

    "account_id": 100624065,
    "name": "AHON44",
    "hero_id": 20,
    "team": 1

},
{

    "account_id": 128632932,
    "name": "Yugi",
    "hero_id": 22,
    "team": 0

},
{

    "account_id": 92706637,
    "name": "ک ɑmз | iAnnihilate",
    "hero_id": 106,
    "team": 1

},
{

    "account_id": 59752811,
    "name": "Bloody Nine",
    "hero_id": 85,
    "team": 0

},
{

    "account_id": 87276347,
    "name": "UNiVeRsE",
    "hero_id": 12,
    "team": 0

},
{

    "account_id": 178465443,
    "name": "xK",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 86726887,
    "name": "MojoStormStout",
    "hero_id": 0,
    "team": 4

},
{

    "account_id": 111051733,
    "name": "傻逼就是话多",
    "hero_id": 30,
    "team": 1

},
{

    "account_id": 220758346,
    "name": "Chigzaj",
    "hero_id": 0,
    "team": 2

},

    {
        "account_id": 86828698,
        "name": "dreK",
        "hero_id": 65,
        "team": 1
    }

],
"lobby_id": 23904643293669924,
"match_id": 1272182368,
"spectators": 16,
"league_id": 2484,
"stream_delay_s": 10,
"radiant_series_wins": 0,
"dire_series_wins": 0,
"series_type": 0,
"league_tier": 1,
"scoreboard":
{

    "duration": 1928.43896484375,
    "roshan_respawn_timer": 540,
    "radiant":

{

    "score": 25,
    "tower_state": 1972,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 22

},
{

    "hero_id": 85

},
{

    "hero_id": 71

},
{

    "hero_id": 12

},

    {
        "hero_id": 90
    }

],
"bans":
[

{

    "hero_id": 57

},
{

    "hero_id": 35

},
{

    "hero_id": 8

},
{

    "hero_id": 61

},

    {
        "hero_id": 17
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 59752811,
    "hero_id": 85,
    "kills": 4,
    "death": 4,
    "assists": 13,
    "last_hits": 45,
    "denies": 4,
    "gold": 504,
    "level": 13,
    "gold_per_min": 242,
    "xp_per_min": 305,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 214,
    "item1": 46,
    "item2": 206,
    "item3": 36,
    "item4": 0,
    "item5": 178,
    "respawn_timer": 0,
    "position_x": -307.9349365234375,
    "position_y": -2094.8671875,
    "net_worth": 6004

},
{

    "player_slot": 2,
    "account_id": 97490608,
    "hero_id": 71,
    "kills": 4,
    "death": 7,
    "assists": 10,
    "last_hits": 46,
    "denies": 0,
    "gold": 738,
    "level": 14,
    "gold_per_min": 263,
    "xp_per_min": 348,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 63,
    "item1": 36,
    "item2": 92,
    "item3": 185,
    "item4": 46,
    "item5": 21,
    "respawn_timer": 0,
    "position_x": -292.35760498046875,
    "position_y": -1683.654296875,
    "net_worth": 6463

},
{

    "player_slot": 3,
    "account_id": 87276347,
    "hero_id": 12,
    "kills": 3,
    "death": 2,
    "assists": 6,
    "last_hits": 265,
    "denies": 6,
    "gold": 2740,
    "level": 21,
    "gold_per_min": 647,
    "xp_per_min": 745,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 41,
    "item1": 65,
    "item2": 143,
    "item3": 174,
    "item4": 147,
    "item5": 63,
    "respawn_timer": 0,
    "position_x": -3067.281982421875,
    "position_y": 116.35295104980469,
    "net_worth": 17940

},
{

    "player_slot": 4,
    "account_id": 128632932,
    "hero_id": 22,
    "kills": 10,
    "death": 9,
    "assists": 9,
    "last_hits": 93,
    "denies": 2,
    "gold": 769,
    "level": 17,
    "gold_per_min": 364,
    "xp_per_min": 495,
    "ultimate_state": 1,
    "ultimate_cooldown": 52,
    "item0": 41,
    "item1": 178,
    "item2": 190,
    "item3": 46,
    "item4": 180,
    "item5": 60,
    "respawn_timer": 0,
    "position_x": 303.9435119628906,
    "position_y": -1893.4102783203125,
    "net_worth": 9689

},

    {
        "player_slot": 5,
        "account_id": 102588710,
        "hero_id": 90,
        "kills": 4,
        "death": 6,
        "assists": 2,
        "last_hits": 105,
        "denies": 2,
        "gold": 901,
        "level": 11,
        "gold_per_min": 289,
        "xp_per_min": 232,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 108,
        "item1": 214,
        "item2": 46,
        "item3": 16,
        "item4": 0,
        "item5": 0,
        "respawn_timer": 0,
        "position_x": 288,
        "position_y": -2386.453857421875,
        "net_worth": 6251
    }

],
"abilities":
[

{

    "ability_id": 5503,
    "ability_level": 4

},
{

    "ability_id": 5472,
    "ability_level": 1

},
{

    "ability_id": 5473,
    "ability_level": 4

},
{

    "ability_id": 5475,
    "ability_level": 2

},
{

    "ability_id": 5476,
    "ability_level": 2

},
{

    "ability_id": 5474,
    "ability_level": 2

},
{

    "ability_id": 5477,
    "ability_level": 4

},
{

    "ability_id": 5471,
    "ability_level": 4

},

        {
            "ability_id": 5479,
            "ability_level": 4
        }
    ]

},
"dire":
{

    "score": 28,
    "tower_state": 1972,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 95

},
{

    "hero_id": 30

},
{

    "hero_id": 20

},
{

    "hero_id": 65

},

    {
        "hero_id": 106
    }

],
"bans":
[

{

    "hero_id": 2

},
{

    "hero_id": 47

},
{

    "hero_id": 26

},
{

    "hero_id": 40

},

    {
        "hero_id": 39
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 86828698,
    "hero_id": 65,
    "kills": 2,
    "death": 6,
    "assists": 13,
    "last_hits": 184,
    "denies": 0,
    "gold": 626,
    "level": 17,
    "gold_per_min": 395,
    "xp_per_min": 494,
    "ultimate_state": 1,
    "ultimate_cooldown": 59,
    "item0": 172,
    "item1": 48,
    "item2": 1,
    "item3": 102,
    "item4": 69,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 603.9434814453125,
    "position_y": -1893.2686767578125,
    "net_worth": 11126

},
{

    "player_slot": 2,
    "account_id": 111051733,
    "hero_id": 30,
    "kills": 0,
    "death": 6,
    "assists": 13,
    "last_hits": 35,
    "denies": 6,
    "gold": 844,
    "level": 13,
    "gold_per_min": 217,
    "xp_per_min": 312,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 36,
    "item1": 73,
    "item2": 21,
    "item3": 29,
    "item4": 46,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 2777.943603515625,
    "position_y": -2083.17724609375,
    "net_worth": 4619

},
{

    "player_slot": 3,
    "account_id": 69256187,
    "hero_id": 95,
    "kills": 3,
    "death": 5,
    "assists": 9,
    "last_hits": 210,
    "denies": 7,
    "gold": 3007,
    "level": 18,
    "gold_per_min": 530,
    "xp_per_min": 571,
    "ultimate_state": 1,
    "ultimate_cooldown": 16,
    "item0": 117,
    "item1": 50,
    "item2": 212,
    "item3": 154,
    "item4": 164,
    "item5": 116,
    "respawn_timer": 0,
    "position_x": 2897.123291015625,
    "position_y": -2356.189697265625,
    "net_worth": 15392

},
{

    "player_slot": 4,
    "account_id": 100624065,
    "hero_id": 20,
    "kills": 3,
    "death": 5,
    "assists": 13,
    "last_hits": 50,
    "denies": 1,
    "gold": 1047,
    "level": 14,
    "gold_per_min": 248,
    "xp_per_min": 333,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 34,
    "item1": 63,
    "item2": 79,
    "item3": 46,
    "item4": 187,
    "item5": 92,
    "respawn_timer": 0,
    "position_x": 1619.302490234375,
    "position_y": -1622.089599609375,
    "net_worth": 7122

},

    {
        "player_slot": 5,
        "account_id": 92706637,
        "hero_id": 106,
        "kills": 19,
        "death": 3,
        "assists": 6,
        "last_hits": 231,
        "denies": 4,
        "gold": 763,
        "level": 22,
        "gold_per_min": 658,
        "xp_per_min": 813,
        "ultimate_state": 1,
        "ultimate_cooldown": 3,
        "item0": 185,
        "item1": 160,
        "item2": 141,
        "item3": 50,
        "item4": 46,
        "item5": 145,
        "respawn_timer": 0,
        "position_x": 1178.762451171875,
        "position_y": 534.2276611328125,
        "net_worth": 19638
    }

],
"abilities":
[

{

    "ability_id": 5603,
    "ability_level": 4

},
{

    "ability_id": 5604,
    "ability_level": 4

},
{

    "ability_id": 5605,
    "ability_level": 4

},
{

    "ability_id": 5607,
    "ability_level": 3

},
{

    "ability_id": 5606,
    "ability_level": 3

},

                {
                    "ability_id": 5002,
                    "ability_level": 7
                }
            ]
        }
    }

},
{

    "players":

[

{

    "account_id": 192098591,
    "name": "mu",
    "hero_id": 0,
    "team": 4

},
{

    "account_id": 116316652,
    "name": "Azumi",
    "hero_id": 0,
    "team": 4

},
{

    "account_id": 86743032,
    "name": "Jonathan",
    "hero_id": 0,
    "team": 4

},
{

    "account_id": 86727555,
    "name": "ppd",
    "hero_id": 78,
    "team": 0

},
{

    "account_id": 59752811,
    "name": "Bloody Nine",
    "hero_id": 1,
    "team": 0

},
{

    "account_id": 25907144,
    "name": "Cr1t-",
    "hero_id": 27,
    "team": 0

},
{

    "account_id": 87276347,
    "name": "UNiVeRsE",
    "hero_id": 13,
    "team": 0

},
{

    "account_id": 128632932,
    "name": "Yugi",
    "hero_id": 16,
    "team": 1

},
{

    "account_id": 86736656,
    "name": "tdm",
    "hero_id": 0,
    "team": 4

},
{

    "account_id": 7910302,
    "name": "sugoi~",
    "hero_id": 20,
    "team": 1

},
{

    "account_id": 100624065,
    "name": "AHON44",
    "hero_id": 54,
    "team": 1

},
{

    "account_id": 11760636,
    "name": "Dollabill",
    "hero_id": 26,
    "team": 0

},
{

    "account_id": 86726887,
    "name": "MojoStormStout",
    "hero_id": 21,
    "team": 1

},
{

    "account_id": 87293485,
    "name": "@zyzzydota",
    "hero_id": 0,
    "team": 4

},

    {
        "account_id": 154094836,
        "name": "again and again",
        "hero_id": 51,
        "team": 1
    }

],
"lobby_id": 23904520841421650,
"match_id": 1272046093,
"spectators": 2,
"league_id": 2484,
"stream_delay_s": 10,
"radiant_series_wins": 0,
"dire_series_wins": 0,
"series_type": 0,
"league_tier": 1,
"scoreboard":
{

    "duration": 2103.8271484375,
    "roshan_respawn_timer": 477,
    "radiant":

{

    "score": 17,
    "tower_state": 1540,
    "barracks_state": 11,
    "picks":

[

{

    "hero_id": 13

},
{

    "hero_id": 26

},
{

    "hero_id": 27

},
{

    "hero_id": 78

},

    {
        "hero_id": 1
    }

],
"bans":
[

{

    "hero_id": 9

},
{

    "hero_id": 10

},
{

    "hero_id": 101

},
{

    "hero_id": 75

},

    {
        "hero_id": 41
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 59752811,
    "hero_id": 1,
    "kills": 9,
    "death": 6,
    "assists": 2,
    "last_hits": 253,
    "denies": 9,
    "gold": 2,
    "level": 21,
    "gold_per_min": 580,
    "xp_per_min": 674,
    "ultimate_state": 1,
    "ultimate_cooldown": 32,
    "item0": 63,
    "item1": 147,
    "item2": 81,
    "item3": 145,
    "item4": 32,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": -3463.900146484375,
    "position_y": -2873.098388671875,
    "net_worth": 14577

},
{

    "player_slot": 2,
    "account_id": 87276347,
    "hero_id": 13,
    "kills": 0,
    "death": 4,
    "assists": 10,
    "last_hits": 163,
    "denies": 4,
    "gold": 2,
    "level": 18,
    "gold_per_min": 403,
    "xp_per_min": 496,
    "ultimate_state": 1,
    "ultimate_cooldown": 44,
    "item0": 0,
    "item1": 60,
    "item2": 102,
    "item3": 1,
    "item4": 41,
    "item5": 63,
    "respawn_timer": 0,
    "position_x": -1293.522705078125,
    "position_y": -2995.917724609375,
    "net_worth": 7852

},
{

    "player_slot": 3,
    "account_id": 86727555,
    "hero_id": 78,
    "kills": 2,
    "death": 11,
    "assists": 6,
    "last_hits": 139,
    "denies": 6,
    "gold": 2,
    "level": 17,
    "gold_per_min": 375,
    "xp_per_min": 479,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 63,
    "item1": 1,
    "item2": 41,
    "item3": 21,
    "item4": 37,
    "item5": 36,
    "respawn_timer": 0,
    "position_x": -4299.5439453125,
    "position_y": -3500.855712890625,
    "net_worth": 7677

},
{

    "player_slot": 4,
    "account_id": 11760636,
    "hero_id": 26,
    "kills": 4,
    "death": 11,
    "assists": 8,
    "last_hits": 37,
    "denies": 1,
    "gold": 5983,
    "level": 13,
    "gold_per_min": 395,
    "xp_per_min": 275,
    "ultimate_state": 1,
    "ultimate_cooldown": 17,
    "item0": 214,
    "item1": 43,
    "item2": 73,
    "item3": 19,
    "item4": 1,
    "item5": 42,
    "respawn_timer": 0,
    "position_x": -2614.736328125,
    "position_y": -4621.47265625,
    "net_worth": 11058

},

    {
        "player_slot": 5,
        "account_id": 25907144,
        "hero_id": 27,
        "kills": 2,
        "death": 6,
        "assists": 4,
        "last_hits": 55,
        "denies": 1,
        "gold": 2,
        "level": 13,
        "gold_per_min": 257,
        "xp_per_min": 260,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 102,
        "item1": 37,
        "item2": 188,
        "item3": 16,
        "item4": 180,
        "item5": 46,
        "respawn_timer": 0,
        "position_x": -5081.625,
        "position_y": -6100.8125,
        "net_worth": 5552
    }

],
"abilities":
[

{

    "ability_id": 5078,
    "ability_level": 4

},
{

    "ability_id": 5079,
    "ability_level": 4

},
{

    "ability_id": 5080,
    "ability_level": 3

},

        {
            "ability_id": 5081,
            "ability_level": 2
        }
    ]

},
"dire":
{

    "score": 38,
    "tower_state": 1972,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 20

},
{

    "hero_id": 51

},
{

    "hero_id": 21

},
{

    "hero_id": 16

},

    {
        "hero_id": 54
    }

],
"bans":
[

{

    "hero_id": 85

},
{

    "hero_id": 22

},
{

    "hero_id": 68

},
{

    "hero_id": 17

},

    {
        "hero_id": 63
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 128632932,
    "hero_id": 16,
    "kills": 7,
    "death": 3,
    "assists": 15,
    "last_hits": 127,
    "denies": 2,
    "gold": 3592,
    "level": 19,
    "gold_per_min": 435,
    "xp_per_min": 588,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 1,
    "item1": 24,
    "item2": 190,
    "item3": 46,
    "item4": 92,
    "item5": 180,
    "respawn_timer": 0,
    "position_x": 3513.59375,
    "position_y": 699.65625,
    "net_worth": 13037

},
{

    "player_slot": 2,
    "account_id": 86726887,
    "hero_id": 21,
    "kills": 18,
    "death": 0,
    "assists": 9,
    "last_hits": 160,
    "denies": 12,
    "gold": 2245,
    "level": 21,
    "gold_per_min": 622,
    "xp_per_min": 667,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 50,
    "item1": 1,
    "item2": 116,
    "item3": 108,
    "item4": 166,
    "item5": 117,
    "respawn_timer": 0,
    "position_x": 7136,
    "position_y": 5920,
    "net_worth": 20820

},
{

    "player_slot": 3,
    "account_id": 100624065,
    "hero_id": 54,
    "kills": 5,
    "death": 3,
    "assists": 8,
    "last_hits": 237,
    "denies": 16,
    "gold": 944,
    "level": 20,
    "gold_per_min": 549,
    "xp_per_min": 629,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 185,
    "item1": 50,
    "item2": 46,
    "item3": 154,
    "item4": 151,
    "item5": 208,
    "respawn_timer": 0,
    "position_x": -607.475341796875,
    "position_y": -521.439453125,
    "net_worth": 17494

},
{

    "player_slot": 4,
    "account_id": 154094836,
    "hero_id": 51,
    "kills": 5,
    "death": 9,
    "assists": 14,
    "last_hits": 93,
    "denies": 2,
    "gold": 233,
    "level": 16,
    "gold_per_min": 362,
    "xp_per_min": 418,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 41,
    "item1": 127,
    "item2": 48,
    "item3": 0,
    "item4": 36,
    "item5": 108,
    "respawn_timer": 0,
    "position_x": 3436.96875,
    "position_y": 2863.40625,
    "net_worth": 10283

},

    {
        "player_slot": 5,
        "account_id": 7910302,
        "hero_id": 20,
        "kills": 3,
        "death": 2,
        "assists": 12,
        "last_hits": 28,
        "denies": 1,
        "gold": 1759,
        "level": 15,
        "gold_per_min": 258,
        "xp_per_min": 354,
        "ultimate_state": 2,
        "ultimate_cooldown": 0,
        "item0": 43,
        "item1": 63,
        "item2": 46,
        "item3": 187,
        "item4": 102,
        "item5": 42,
        "respawn_timer": 23,
        "position_x": -2266.2734375,
        "position_y": -2814.681396484375,
        "net_worth": 7059
    }

],
"abilities":
[

{

    "ability_id": 5122,
    "ability_level": 4

},
{

    "ability_id": 5124,
    "ability_level": 4

},
{

    "ability_id": 5123,
    "ability_level": 4

},
{

    "ability_id": 5125,
    "ability_level": 2

},

                {
                    "ability_id": 5002,
                    "ability_level": 1
                }
            ]
        }
    }

},
{

    "players":

[

{

    "account_id": 32895399,
    "name": "Tzar",
    "hero_id": 0,
    "team": 4

},
{

    "account_id": 79788025,
    "name": "dingdangu [b]",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 91982026,
    "name": "Hook-^^,SOLO",
    "hero_id": 13,
    "team": 1

},
{

    "account_id": 91751637,
    "name": "Arry oberyanoo",
    "hero_id": 33,
    "team": 1

},
{

    "account_id": 99326103,
    "name": "111111",
    "hero_id": 96,
    "team": 1

},
{

    "account_id": 96169991,
    "name": "Ar1se^-",
    "hero_id": 99,
    "team": 0

},
{

    "account_id": 49842719,
    "name": "-_-",
    "hero_id": 26,
    "team": 1

},
{

    "account_id": 88271237,
    "name": "madshka",
    "hero_id": 22,
    "team": 0

},
{

    "account_id": 86700461,
    "name": "w33",
    "hero_id": 86,
    "team": 0

},
{

    "account_id": 87285329,
    "name": "Pajkatt",
    "hero_id": 39,
    "team": 0

},
{

    "account_id": 100166910,
    "name": "let it go ! la la!",
    "hero_id": 71,
    "team": 0

},
{

    "account_id": 115914180,
    "name": "YOLOO BOYZZZZZZZZZZZ",
    "hero_id": 8,
    "team": 1

},

    {
        "account_id": 29024264,
        "name": "FreshPro / WraLth / FreshFriFly",
        "hero_id": 0,
        "team": 2
    }

],
"dire_team":
{

    "team_name": "4 Bunnies 1 Turtle.",
    "team_id": 1859971,
    "team_logo": 35223031181460490,
    "complete": false

},
"lobby_id": 23901792918143824,
"match_id": 1271860703,
"spectators": 1,
"league_id": 2470,
"stream_delay_s": 120,
"radiant_series_wins": 0,
"dire_series_wins": 0,
"series_type": 0,
"league_tier": 1,
"scoreboard":
{

    "duration": 918.0758056640625,
    "roshan_respawn_timer": 0,
    "radiant":

{

    "score": 19,
    "tower_state": 2047,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 99

},
{

    "hero_id": 86

},
{

    "hero_id": 71

},
{

    "hero_id": 39

},

    {
        "hero_id": 22
    }

],
"bans":
[

{

    "hero_id": 2

},
{

    "hero_id": 95

},
{

    "hero_id": 61

},
{

    "hero_id": 65

},

    {
        "hero_id": 20
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 87285329,
    "hero_id": 39,
    "kills": 8,
    "death": 2,
    "assists": 5,
    "last_hits": 26,
    "denies": 0,
    "gold": 700,
    "level": 9,
    "gold_per_min": 355,
    "xp_per_min": 334,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 63,
    "item1": 36,
    "item2": 188,
    "item3": 92,
    "item4": 57,
    "item5": 46,
    "respawn_timer": 0,
    "position_x": 3784.1650390625,
    "position_y": 1006.6646728515625,
    "net_worth": 4550

},
{

    "player_slot": 2,
    "account_id": 100166910,
    "hero_id": 71,
    "kills": 3,
    "death": 3,
    "assists": 6,
    "last_hits": 39,
    "denies": 2,
    "gold": 308,
    "level": 10,
    "gold_per_min": 304,
    "xp_per_min": 362,
    "ultimate_state": 1,
    "ultimate_cooldown": 54,
    "item0": 63,
    "item1": 185,
    "item2": 34,
    "item3": 181,
    "item4": 182,
    "item5": 46,
    "respawn_timer": 0,
    "position_x": 3638.974365234375,
    "position_y": 880.6443481445312,
    "net_worth": 4383

},
{

    "player_slot": 3,
    "account_id": 88271237,
    "hero_id": 22,
    "kills": 2,
    "death": 0,
    "assists": 10,
    "last_hits": 76,
    "denies": 3,
    "gold": 185,
    "level": 11,
    "gold_per_min": 422,
    "xp_per_min": 446,
    "ultimate_state": 1,
    "ultimate_cooldown": 62,
    "item0": 100,
    "item1": 41,
    "item2": 180,
    "item3": 36,
    "item4": 60,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 1322.79345703125,
    "position_y": 1237.6304931640625,
    "net_worth": 6885

},
{

    "player_slot": 4,
    "account_id": 86700461,
    "hero_id": 86,
    "kills": 3,
    "death": 0,
    "assists": 8,
    "last_hits": 6,
    "denies": 0,
    "gold": 254,
    "level": 9,
    "gold_per_min": 224,
    "xp_per_min": 335,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 28,
    "item1": 57,
    "item2": 46,
    "item3": 43,
    "item4": 214,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 116.5902328491211,
    "position_y": 1863.5721435546875,
    "net_worth": 2754

},

    {
        "player_slot": 5,
        "account_id": 96169991,
        "hero_id": 99,
        "kills": 2,
        "death": 1,
        "assists": 7,
        "last_hits": 75,
        "denies": 7,
        "gold": 538,
        "level": 11,
        "gold_per_min": 396,
        "xp_per_min": 493,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 63,
        "item1": 34,
        "item2": 46,
        "item3": 17,
        "item4": 21,
        "item5": 125,
        "respawn_timer": 0,
        "position_x": 6261.59326171875,
        "position_y": -1955.1732177734375,
        "net_worth": 6088
    }

],
"abilities":
[

{

    "ability_id": 5548,
    "ability_level": 2

},
{

    "ability_id": 5549,
    "ability_level": 4

},
{

    "ability_id": 5550,
    "ability_level": 3

},

        {
            "ability_id": 5551,
            "ability_level": 2
        }
    ]

},
"dire":
{

    "score": 6,
    "tower_state": 2039,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 8

},
{

    "hero_id": 26

},
{

    "hero_id": 96

},
{

    "hero_id": 13

},

    {
        "hero_id": 33
    }

],
"bans":
[

{

    "hero_id": 82

},
{

    "hero_id": 35

},
{

    "hero_id": 50

},
{

    "hero_id": 91

},

    {
        "hero_id": 11
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 115914180,
    "hero_id": 8,
    "kills": 1,
    "death": 4,
    "assists": 2,
    "last_hits": 62,
    "denies": 10,
    "gold": 373,
    "level": 9,
    "gold_per_min": 298,
    "xp_per_min": 318,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 26,
    "item1": 50,
    "item2": 182,
    "item3": 212,
    "item4": 46,
    "item5": 0,
    "respawn_timer": 14,
    "position_x": -1269.8516845703125,
    "position_y": 3667.255126953125,
    "net_worth": 3983

},
{

    "player_slot": 2,
    "account_id": 49842719,
    "hero_id": 26,
    "kills": 0,
    "death": 6,
    "assists": 4,
    "last_hits": 9,
    "denies": 2,
    "gold": 52,
    "level": 7,
    "gold_per_min": 144,
    "xp_per_min": 177,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 29,
    "item1": 188,
    "item2": 34,
    "item3": 16,
    "item4": 16,
    "item5": 27,
    "respawn_timer": 0,
    "position_x": 7040,
    "position_y": 6408,
    "net_worth": 1252

},
{

    "player_slot": 3,
    "account_id": 91751637,
    "hero_id": 33,
    "kills": 0,
    "death": 3,
    "assists": 1,
    "last_hits": 69,
    "denies": 2,
    "gold": 397,
    "level": 8,
    "gold_per_min": 288,
    "xp_per_min": 266,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 86,
    "item1": 46,
    "item2": 0,
    "item3": 178,
    "item4": 29,
    "item5": 94,
    "respawn_timer": 0,
    "position_x": 6723.84228515625,
    "position_y": 3279.2060546875,
    "net_worth": 3147

},
{

    "player_slot": 4,
    "account_id": 99326103,
    "hero_id": 96,
    "kills": 2,
    "death": 3,
    "assists": 1,
    "last_hits": 55,
    "denies": 4,
    "gold": 50,
    "level": 9,
    "gold_per_min": 286,
    "xp_per_min": 289,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 1,
    "item1": 0,
    "item2": 0,
    "item3": 34,
    "item4": 214,
    "item5": 182,
    "respawn_timer": 0,
    "position_x": 3797.30224609375,
    "position_y": 4616.6357421875,
    "net_worth": 3750

},

    {
        "player_slot": 5,
        "account_id": 91982026,
        "hero_id": 13,
        "kills": 2,
        "death": 3,
        "assists": 3,
        "last_hits": 54,
        "denies": 3,
        "gold": 1290,
        "level": 10,
        "gold_per_min": 330,
        "xp_per_min": 353,
        "ultimate_state": 1,
        "ultimate_cooldown": 67,
        "item0": 41,
        "item1": 77,
        "item2": 36,
        "item3": 0,
        "item4": 0,
        "item5": 63,
        "respawn_timer": 0,
        "position_x": 3759.809326171875,
        "position_y": 1519.4141845703125,
        "net_worth": 4360
    }

],
"abilities":
[

{

    "ability_id": 5069,
    "ability_level": 4

},
{

    "ability_id": 5071,
    "ability_level": 4

},
{

    "ability_id": 5072,
    "ability_level": 1

},
{

    "ability_id": 5070,
    "ability_level": 4

},

                {
                    "ability_id": 5073,
                    "ability_level": 1
                }
            ]
        }
    }

},
{

    "players":

[

{

    "account_id": 99326103,
    "name": "111111",
    "hero_id": 26,
    "team": 0

},
{

    "account_id": 90423751,
    "name": "Bignum",
    "hero_id": 35,
    "team": 1

},
{

    "account_id": 91932652,
    "name": "Flow <3 Christie",
    "hero_id": 85,
    "team": 0

},
{

    "account_id": 86890460,
    "name": "112233",
    "hero_id": 99,
    "team": 1

},
{

    "account_id": 49842719,
    "name": "-_-",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 169342082,
    "name": "dread_go_stream_zaeb",
    "hero_id": 28,
    "team": 0

},
{

    "account_id": 198097951,
    "name": "Axypa-_-",
    "hero_id": 50,
    "team": 1

},
{

    "account_id": 89945143,
    "name": "PosingAsMe",
    "hero_id": 69,
    "team": 0

},
{

    "account_id": 166321067,
    "name": "Sora",
    "hero_id": 7,
    "team": 1

},
{

    "account_id": 123444610,
    "name": "MeTTpuM",
    "hero_id": 17,
    "team": 1

},

    {
        "account_id": 61845310,
        "name": "lll",
        "hero_id": 21,
        "team": 0
    }

],
"lobby_id": 23904643293085180,
"match_id": 1272180899,
"spectators": 3,
"league_id": 2470,
"stream_delay_s": 120,
"radiant_series_wins": 0,
"dire_series_wins": 0,
"series_type": 0,
"league_tier": 1,
"scoreboard":
{

    "duration": 2310.763671875,
    "roshan_respawn_timer": 166,
    "radiant":

{

    "score": 37,
    "tower_state": 1972,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 26

},
{

    "hero_id": 28

},
{

    "hero_id": 69

},
{

    "hero_id": 21

},

    {
        "hero_id": 85
    }

],
"bans":
[

{

    "hero_id": 2

},
{

    "hero_id": 20

},
{

    "hero_id": 39

},
{

    "hero_id": 71

},

    {
        "hero_id": 33
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 61845310,
    "hero_id": 21,
    "kills": 6,
    "death": 4,
    "assists": 12,
    "last_hits": 199,
    "denies": 21,
    "gold": 893,
    "level": 20,
    "gold_per_min": 451,
    "xp_per_min": 577,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 116,
    "item1": 108,
    "item2": 1,
    "item3": 50,
    "item4": 46,
    "item5": 166,
    "respawn_timer": 0,
    "position_x": -4921.3984375,
    "position_y": -5438.3037109375,
    "net_worth": 15568

},
{

    "player_slot": 2,
    "account_id": 169342082,
    "hero_id": 28,
    "kills": 6,
    "death": 5,
    "assists": 18,
    "last_hits": 99,
    "denies": 13,
    "gold": 2852,
    "level": 19,
    "gold_per_min": 344,
    "xp_per_min": 531,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 1,
    "item1": 63,
    "item2": 116,
    "item3": 0,
    "item4": 36,
    "item5": 46,
    "respawn_timer": 29,
    "position_x": 3240.248779296875,
    "position_y": 2134.587646484375,
    "net_worth": 11077

},
{

    "player_slot": 3,
    "account_id": 91932652,
    "hero_id": 85,
    "kills": 8,
    "death": 4,
    "assists": 14,
    "last_hits": 97,
    "denies": 6,
    "gold": 207,
    "level": 18,
    "gold_per_min": 393,
    "xp_per_min": 444,
    "ultimate_state": 1,
    "ultimate_cooldown": 15,
    "item0": 203,
    "item1": 92,
    "item2": 65,
    "item3": 0,
    "item4": 0,
    "item5": 127,
    "respawn_timer": 0,
    "position_x": -2214.091552734375,
    "position_y": -1836.50146484375,
    "net_worth": 13652

},
{

    "player_slot": 4,
    "account_id": 89945143,
    "hero_id": 69,
    "kills": 9,
    "death": 7,
    "assists": 13,
    "last_hits": 134,
    "denies": 2,
    "gold": 749,
    "level": 17,
    "gold_per_min": 457,
    "xp_per_min": 432,
    "ultimate_state": 1,
    "ultimate_cooldown": 25,
    "item0": 50,
    "item1": 1,
    "item2": 116,
    "item3": 185,
    "item4": 36,
    "item5": 108,
    "respawn_timer": 6,
    "position_x": 1770.276611328125,
    "position_y": 62.89779281616211,
    "net_worth": 14874

},

    {
        "player_slot": 5,
        "account_id": 99326103,
        "hero_id": 26,
        "kills": 5,
        "death": 7,
        "assists": 15,
        "last_hits": 32,
        "denies": 2,
        "gold": 890,
        "level": 15,
        "gold_per_min": 242,
        "xp_per_min": 333,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 1,
        "item1": 36,
        "item2": 46,
        "item3": 42,
        "item4": 21,
        "item5": 214,
        "respawn_timer": 0,
        "position_x": -5121.6513671875,
        "position_y": -5611.84814453125,
        "net_worth": 5890
    }

],
"abilities":
[

{

    "ability_id": 5044,
    "ability_level": 4

},
{

    "ability_id": 5045,
    "ability_level": 4

},
{

    "ability_id": 5046,
    "ability_level": 4

},
{

    "ability_id": 5047,
    "ability_level": 2

},

        {
            "ability_id": 5002,
            "ability_level": 1
        }
    ]

},
"dire":
{

    "score": 27,
    "tower_state": 1830,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 99

},
{

    "hero_id": 50

},
{

    "hero_id": 17

},
{

    "hero_id": 35

},

    {
        "hero_id": 7
    }

],
"bans":
[

{

    "hero_id": 95

},
{

    "hero_id": 8

},
{

    "hero_id": 25

},
{

    "hero_id": 29

},

    {
        "hero_id": 101
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 123444610,
    "hero_id": 17,
    "kills": 3,
    "death": 9,
    "assists": 12,
    "last_hits": 115,
    "denies": 14,
    "gold": 627,
    "level": 15,
    "gold_per_min": 306,
    "xp_per_min": 317,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 63,
    "item1": 98,
    "item2": 36,
    "item3": 41,
    "item4": 21,
    "item5": 46,
    "respawn_timer": 0,
    "position_x": 4039.724609375,
    "position_y": 3652.498779296875,
    "net_worth": 8452

},
{

    "player_slot": 2,
    "account_id": 198097951,
    "hero_id": 50,
    "kills": 1,
    "death": 8,
    "assists": 3,
    "last_hits": 56,
    "denies": 7,
    "gold": 416,
    "level": 13,
    "gold_per_min": 207,
    "xp_per_min": 262,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 0,
    "item1": 214,
    "item2": 36,
    "item3": 187,
    "item4": 0,
    "item5": 178,
    "respawn_timer": 0,
    "position_x": 6008.234375,
    "position_y": 4984.50732421875,
    "net_worth": 4816

},
{

    "player_slot": 3,
    "account_id": 90423751,
    "hero_id": 35,
    "kills": 17,
    "death": 4,
    "assists": 2,
    "last_hits": 211,
    "denies": 20,
    "gold": 1426,
    "level": 22,
    "gold_per_min": 565,
    "xp_per_min": 705,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 50,
    "item1": 154,
    "item2": 46,
    "item3": 160,
    "item4": 172,
    "item5": 135,
    "respawn_timer": 25,
    "position_x": 1636.2078857421875,
    "position_y": 89.69075775146484,
    "net_worth": 19851

},
{

    "player_slot": 4,
    "account_id": 166321067,
    "hero_id": 7,
    "kills": 2,
    "death": 9,
    "assists": 12,
    "last_hits": 71,
    "denies": 1,
    "gold": 549,
    "level": 14,
    "gold_per_min": 242,
    "xp_per_min": 277,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 178,
    "item1": 102,
    "item2": 214,
    "item3": 1,
    "item4": 46,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 5430.84521484375,
    "position_y": 4112.05322265625,
    "net_worth": 6949

},

    {
        "player_slot": 5,
        "account_id": 86890460,
        "hero_id": 99,
        "kills": 4,
        "death": 7,
        "assists": 9,
        "last_hits": 190,
        "denies": 21,
        "gold": 729,
        "level": 18,
        "gold_per_min": 370,
        "xp_per_min": 478,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 127,
        "item1": 36,
        "item2": 125,
        "item3": 63,
        "item4": 112,
        "item5": 46,
        "respawn_timer": 25,
        "position_x": 3151.92431640625,
        "position_y": 2011.9588623046875,
        "net_worth": 12404
    }

],
"abilities":
[

{

    "ability_id": 5548,
    "ability_level": 4

},
{

    "ability_id": 5549,
    "ability_level": 4

},
{

    "ability_id": 5550,
    "ability_level": 4

},
{

    "ability_id": 5551,
    "ability_level": 3

},

                {
                    "ability_id": 5002,
                    "ability_level": 3
                }
            ]
        }
    }

},
{

    "players":

[

{

    "account_id": 102581463,
    "name": "Subs Zen",
    "hero_id": 86,
    "team": 1

},
{

    "account_id": 66610015,
    "name": "HTF|BeniTesz",
    "hero_id": 9,
    "team": 1

},
{

    "account_id": 133907787,
    "name": ".l. elzinhoo'",
    "hero_id": 17,
    "team": 1

},
{

    "account_id": 103911729,
    "name": "Cerberus.Black",
    "hero_id": 45,
    "team": 0

},
{

    "account_id": 157065989,
    "name": "Cerberus.^J@P@ ツ",
    "hero_id": 8,
    "team": 0

},
{

    "account_id": 151542087,
    "name": "aLyy",
    "hero_id": 41,
    "team": 1

},
{

    "account_id": 114643420,
    "name": "Cerberus.Sk@t|ON",
    "hero_id": 30,
    "team": 0

},
{

    "account_id": 3019591,
    "name": "bnz",
    "hero_id": 2,
    "team": 0

},
{

    "account_id": 107043543,
    "name": "KuramA431",
    "hero_id": 26,
    "team": 0

},

    {
        "account_id": 102584839,
        "name": "Blanka",
        "hero_id": 7,
        "team": 1
    }

],
"radiant_team":
{

    "team_name": "Cerberus e-Sports",
    "team_id": 1197290,
    "team_logo": 38608076489498260,
    "complete": false

},
"dire_team":
{

    "team_name": "Da Raduquem Ryu",
    "team_id": 2143420,
    "team_logo": 0,
    "complete": false

},
"lobby_id": 23904643302245970,
"match_id": 1272208391,
"spectators": 1,
"league_id": 2469,
"stream_delay_s": 120,
"radiant_series_wins": 0,
"dire_series_wins": 0,
"series_type": 0,
"league_tier": 1,
"scoreboard":
{

    "duration": 510.9085693359375,
    "roshan_respawn_timer": 0,
    "radiant":

{

    "score": 4,
    "tower_state": 2047,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 2

},
{

    "hero_id": 26

},
{

    "hero_id": 30

},
{

    "hero_id": 8

},

    {
        "hero_id": 45
    }

],
"bans":
[

{

    "hero_id": 95

},
{

    "hero_id": 99

},
{

    "hero_id": 35

},
{

    "hero_id": 78

},

    {
        "hero_id": 76
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 103911729,
    "hero_id": 45,
    "kills": 0,
    "death": 1,
    "assists": 1,
    "last_hits": 27,
    "denies": 7,
    "gold": 610,
    "level": 7,
    "gold_per_min": 373,
    "xp_per_min": 305,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 16,
    "item1": 16,
    "item2": 77,
    "item3": 29,
    "item4": 60,
    "item5": 41,
    "respawn_timer": 0,
    "position_x": 1783.413818359375,
    "position_y": 1520.95068359375,
    "net_worth": 3560

},
{

    "player_slot": 2,
    "account_id": 157065989,
    "hero_id": 8,
    "kills": 1,
    "death": 0,
    "assists": 0,
    "last_hits": 22,
    "denies": 2,
    "gold": 769,
    "level": 7,
    "gold_per_min": 326,
    "xp_per_min": 366,
    "ultimate_state": 1,
    "ultimate_cooldown": 28,
    "item0": 0,
    "item1": 212,
    "item2": 50,
    "item3": 16,
    "item4": 16,
    "item5": 16,
    "respawn_timer": 0,
    "position_x": 1877.730712890625,
    "position_y": 1295.632080078125,
    "net_worth": 3279

},
{

    "player_slot": 3,
    "account_id": 114643420,
    "hero_id": 30,
    "kills": 1,
    "death": 0,
    "assists": 2,
    "last_hits": 3,
    "denies": 1,
    "gold": 285,
    "level": 4,
    "gold_per_min": 237,
    "xp_per_min": 137,
    "ultimate_state": 0,
    "ultimate_cooldown": 0,
    "item0": 180,
    "item1": 44,
    "item2": 46,
    "item3": 16,
    "item4": 16,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 1530.5430908203125,
    "position_y": 2273.6689453125,
    "net_worth": 2160

},
{

    "player_slot": 4,
    "account_id": 107043543,
    "hero_id": 26,
    "kills": 0,
    "death": 0,
    "assists": 1,
    "last_hits": 2,
    "denies": 0,
    "gold": 653,
    "level": 4,
    "gold_per_min": 194,
    "xp_per_min": 148,
    "ultimate_state": 0,
    "ultimate_cooldown": 0,
    "item0": 0,
    "item1": 188,
    "item2": 44,
    "item3": 0,
    "item4": 16,
    "item5": 29,
    "respawn_timer": 0,
    "position_x": 2045.6287841796875,
    "position_y": 1278.1748046875,
    "net_worth": 1678

},

    {
        "player_slot": 5,
        "account_id": 3019591,
        "hero_id": 2,
        "kills": 2,
        "death": 0,
        "assists": 2,
        "last_hits": 56,
        "denies": 2,
        "gold": 516,
        "level": 8,
        "gold_per_min": 547,
        "xp_per_min": 412,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 214,
        "item1": 182,
        "item2": 1,
        "item3": 19,
        "item4": 16,
        "item5": 4,
        "respawn_timer": 0,
        "position_x": 5782.8173828125,
        "position_y": -2939.879638671875,
        "net_worth": 5066
    }

],
"abilities":
[

{

    "ability_id": 5007,
    "ability_level": 2

},
{

    "ability_id": 5008,
    "ability_level": 1

},
{

    "ability_id": 5009,
    "ability_level": 4

},

        {
            "ability_id": 5010,
            "ability_level": 1
        }
    ]

},
"dire":
{

    "score": 1,
    "tower_state": 2036,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 7

},
{

    "hero_id": 86

},
{

    "hero_id": 41

},
{

    "hero_id": 9

},

    {
        "hero_id": 17
    }

],
"bans":
[

{

    "hero_id": 29

},
{

    "hero_id": 65

},
{

    "hero_id": 43

},
{

    "hero_id": 50

},

    {
        "hero_id": 74
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 151542087,
    "hero_id": 41,
    "kills": 0,
    "death": 2,
    "assists": 0,
    "last_hits": 26,
    "denies": 0,
    "gold": 1367,
    "level": 6,
    "gold_per_min": 232,
    "xp_per_min": 273,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 11,
    "item1": 16,
    "item2": 0,
    "item3": 25,
    "item4": 0,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": -2059.5751953125,
    "position_y": 5930.93212890625,
    "net_worth": 2142

},
{

    "player_slot": 2,
    "account_id": 102584839,
    "hero_id": 7,
    "kills": 0,
    "death": 0,
    "assists": 0,
    "last_hits": 1,
    "denies": 0,
    "gold": 75,
    "level": 3,
    "gold_per_min": 105,
    "xp_per_min": 80,
    "ultimate_state": 0,
    "ultimate_cooldown": 0,
    "item0": 0,
    "item1": 44,
    "item2": 29,
    "item3": 0,
    "item4": 0,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 3361.0625,
    "position_y": 1699.5,
    "net_worth": 750

},
{

    "player_slot": 3,
    "account_id": 102581463,
    "hero_id": 86,
    "kills": 0,
    "death": 1,
    "assists": 0,
    "last_hits": 3,
    "denies": 1,
    "gold": 35,
    "level": 4,
    "gold_per_min": 110,
    "xp_per_min": 136,
    "ultimate_state": 0,
    "ultimate_cooldown": 0,
    "item0": 188,
    "item1": 0,
    "item2": 34,
    "item3": 44,
    "item4": 0,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 2333.59375,
    "position_y": 3301.96875,
    "net_worth": 910

},
{

    "player_slot": 4,
    "account_id": 133907787,
    "hero_id": 17,
    "kills": 1,
    "death": 1,
    "assists": 0,
    "last_hits": 16,
    "denies": 3,
    "gold": 854,
    "level": 6,
    "gold_per_min": 226,
    "xp_per_min": 281,
    "ultimate_state": 0,
    "ultimate_cooldown": 0,
    "item0": 41,
    "item1": 16,
    "item2": 16,
    "item3": 16,
    "item4": 29,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 3117.1025390625,
    "position_y": 2223.6904296875,
    "net_worth": 2154

},

    {
        "player_slot": 5,
        "account_id": 66610015,
        "hero_id": 9,
        "kills": 0,
        "death": 0,
        "assists": 0,
        "last_hits": 44,
        "denies": 12,
        "gold": 144,
        "level": 6,
        "gold_per_min": 321,
        "xp_per_min": 300,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 212,
        "item1": 0,
        "item2": 73,
        "item3": 50,
        "item4": 46,
        "item5": 0,
        "respawn_timer": 0,
        "position_x": 6462.146484375,
        "position_y": -1218.22802734375,
        "net_worth": 3129
    }

],
"abilities":
[

{

    "ability_id": 5051,
    "ability_level": 1

},
{

    "ability_id": 5048,
    "ability_level": 3

},
{

    "ability_id": 5050,
    "ability_level": 1

},

                {
                    "ability_id": 5049,
                    "ability_level": 1
                }
            ]
        }
    }

},
{

    "players":

[

{

    "account_id": 1024342,
    "name": "D2CanadaCup|Joker",
    "hero_id": 0,
    "team": 4

},
{

    "account_id": 80542879,
    "name": "@AdekvatTV",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 100175472,
    "name": "noob",
    "hero_id": 20,
    "team": 1

},
{

    "account_id": 8587184,
    "name": "Rotnam",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 85805514,
    "name": "DeMoN",
    "hero_id": 22,
    "team": 0

},
{

    "account_id": 88271237,
    "name": "madshka",
    "hero_id": 26,
    "team": 0

},
{

    "account_id": 194521913,
    "name": "Kagami Taiga",
    "hero_id": 8,
    "team": 1

},
{

    "account_id": 109455705,
    "name": "F",
    "hero_id": 97,
    "team": 1

},
{

    "account_id": 31818853,
    "name": "BRAX",
    "hero_id": 39,
    "team": 0

},
{

    "account_id": 105178768,
    "name": "BananaSlamJamma",
    "hero_id": 77,
    "team": 0

},
{

    "account_id": 100507647,
    "name": "Nightmare",
    "hero_id": 87,
    "team": 1

},
{

    "account_id": 153671,
    "name": "miraclechipmunk",
    "hero_id": 110,
    "team": 0

},
{

    "account_id": 58942867,
    "name": "nobusada [gong xi fa cai]",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 133786275,
    "name": "@S treetlightdota",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 70090192,
    "name": "MotPax",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 26916833,
    "name": "WhatIsHip",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 91366970,
    "name": "PEW PEW PEW",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 12196957,
    "name": "Maut",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 90586451,
    "name": "Dhaneesi",
    "hero_id": 0,
    "team": 2

},
{

    "account_id": 101054160,
    "name": "GSTV@Imperius",
    "hero_id": 0,
    "team": 2

},

    {
        "account_id": 91364275,
        "name": "√ Kohina Hiruko",
        "hero_id": 11,
        "team": 1
    }

],
"radiant_team":
{

    "team_name": "Champions of Summer's Rift",
    "team_id": 2162587,
    "team_logo": 27356777995381748,
    "complete": true

},
"dire_team":
{

    "team_name": "Union Gaming PE",
    "team_id": 720700,
    "team_logo": 486696207764361400,
    "complete": true

},
"lobby_id": 23904643299289150,
"match_id": 1272200305,
"spectators": 230,
"league_id": 2377,
"stream_delay_s": 300,
"radiant_series_wins": 1,
"dire_series_wins": 0,
"series_type": 1,
"league_tier": 2,
"scoreboard":
{

    "duration": 1258.9259033203125,
    "roshan_respawn_timer": 470,
    "radiant":

{

    "score": 14,
    "tower_state": 1974,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 26

},
{

    "hero_id": 22

},
{

    "hero_id": 110

},
{

    "hero_id": 77

},

    {
        "hero_id": 39
    }

],
"bans":
[

{

    "hero_id": 47

},
{

    "hero_id": 51

},
{

    "hero_id": 29

},
{

    "hero_id": 33

},

    {
        "hero_id": 61
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 31818853,
    "hero_id": 39,
    "kills": 6,
    "death": 1,
    "assists": 4,
    "last_hits": 103,
    "denies": 15,
    "gold": 459,
    "level": 14,
    "gold_per_min": 446,
    "xp_per_min": 545,
    "ultimate_state": 1,
    "ultimate_cooldown": 8,
    "item0": 98,
    "item1": 36,
    "item2": 77,
    "item3": 63,
    "item4": 41,
    "item5": 46,
    "respawn_timer": 0,
    "position_x": 2458.319091796875,
    "position_y": -7072,
    "net_worth": 8954

},
{

    "player_slot": 2,
    "account_id": 105178768,
    "hero_id": 77,
    "kills": 2,
    "death": 1,
    "assists": 4,
    "last_hits": 187,
    "denies": 13,
    "gold": 800,
    "level": 14,
    "gold_per_min": 550,
    "xp_per_min": 557,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 63,
    "item1": 55,
    "item2": 81,
    "item3": 65,
    "item4": 11,
    "item5": 4,
    "respawn_timer": 0,
    "position_x": -1206.6944580078125,
    "position_y": -1824.83251953125,
    "net_worth": 10500

},
{

    "player_slot": 3,
    "account_id": 85805514,
    "hero_id": 22,
    "kills": 3,
    "death": 4,
    "assists": 5,
    "last_hits": 28,
    "denies": 0,
    "gold": 1911,
    "level": 9,
    "gold_per_min": 228,
    "xp_per_min": 219,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 42,
    "item1": 0,
    "item2": 0,
    "item3": 214,
    "item4": 16,
    "item5": 178,
    "respawn_timer": 0,
    "position_x": -6023.84765625,
    "position_y": 3037.518310546875,
    "net_worth": 3911

},
{

    "player_slot": 4,
    "account_id": 88271237,
    "hero_id": 26,
    "kills": 2,
    "death": 3,
    "assists": 3,
    "last_hits": 42,
    "denies": 6,
    "gold": 908,
    "level": 11,
    "gold_per_min": 251,
    "xp_per_min": 330,
    "ultimate_state": 1,
    "ultimate_cooldown": 1,
    "item0": 1,
    "item1": 46,
    "item2": 214,
    "item3": 25,
    "item4": 0,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": -3339.786376953125,
    "position_y": 1410.0631103515625,
    "net_worth": 4758

},

    {
        "player_slot": 5,
        "account_id": 153671,
        "hero_id": 110,
        "kills": 0,
        "death": 2,
        "assists": 5,
        "last_hits": 35,
        "denies": 11,
        "gold": 1705,
        "level": 10,
        "gold_per_min": 199,
        "xp_per_min": 277,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 214,
        "item1": 41,
        "item2": 16,
        "item3": 16,
        "item4": 46,
        "item5": 34,
        "respawn_timer": 0,
        "position_x": -4435.31982421875,
        "position_y": -4503.35205078125,
        "net_worth": 3805
    }

],
"abilities":
[

{

    "ability_id": 5623,
    "ability_level": 1

},
{

    "ability_id": 5625,
    "ability_level": 4

},
{

    "ability_id": 5626,
    "ability_level": 4

},
{

    "ability_id": 5630,
    "ability_level": 1

},
{

    "ability_id": 5631,
    "ability_level": 4

},
{

    "ability_id": 5624,
    "ability_level": 1

},
{

    "ability_id": 5627,
    "ability_level": 4

},

        {
            "ability_id": 5628,
            "ability_level": 4
        }
    ]

},
"dire":
{

    "score": 11,
    "tower_state": 2047,
    "barracks_state": 63,
    "picks":

[

{

    "hero_id": 20

},
{

    "hero_id": 8

},
{

    "hero_id": 87

},
{

    "hero_id": 97

},

    {
        "hero_id": 11
    }

],
"bans":
[

{

    "hero_id": 65

},
{

    "hero_id": 2

},
{

    "hero_id": 95

},
{

    "hero_id": 93

},

    {
        "hero_id": 46
    }

],
"players":
[

{

    "player_slot": 1,
    "account_id": 194521913,
    "hero_id": 8,
    "kills": 3,
    "death": 1,
    "assists": 1,
    "last_hits": 179,
    "denies": 24,
    "gold": 3137,
    "level": 15,
    "gold_per_min": 606,
    "xp_per_min": 623,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 50,
    "item1": 172,
    "item2": 11,
    "item3": 212,
    "item4": 147,
    "item5": 117,
    "respawn_timer": 0,
    "position_x": 3063.780029296875,
    "position_y": -6193.5205078125,
    "net_worth": 12472

},
{

    "player_slot": 2,
    "account_id": 100507647,
    "hero_id": 87,
    "kills": 0,
    "death": 3,
    "assists": 5,
    "last_hits": 14,
    "denies": 1,
    "gold": 974,
    "level": 8,
    "gold_per_min": 157,
    "xp_per_min": 189,
    "ultimate_state": 1,
    "ultimate_cooldown": 33,
    "item0": 34,
    "item1": 92,
    "item2": 0,
    "item3": 16,
    "item4": 29,
    "item5": 0,
    "respawn_timer": 0,
    "position_x": 74.35246276855469,
    "position_y": -54.073726654052734,
    "net_worth": 2549

},
{

    "player_slot": 3,
    "account_id": 109455705,
    "hero_id": 97,
    "kills": 3,
    "death": 1,
    "assists": 4,
    "last_hits": 49,
    "denies": 0,
    "gold": 335,
    "level": 11,
    "gold_per_min": 302,
    "xp_per_min": 373,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 36,
    "item1": 41,
    "item2": 1,
    "item3": 29,
    "item4": 46,
    "item5": 27,
    "respawn_timer": 0,
    "position_x": 1768.2930908203125,
    "position_y": -3828.732421875,
    "net_worth": 5585

},
{

    "player_slot": 4,
    "account_id": 100175472,
    "hero_id": 20,
    "kills": 1,
    "death": 5,
    "assists": 5,
    "last_hits": 7,
    "denies": 1,
    "gold": 101,
    "level": 8,
    "gold_per_min": 153,
    "xp_per_min": 196,
    "ultimate_state": 3,
    "ultimate_cooldown": 0,
    "item0": 29,
    "item1": 188,
    "item2": 43,
    "item3": 36,
    "item4": 42,
    "item5": 46,
    "respawn_timer": 0,
    "position_x": 3839.7841796875,
    "position_y": -3758.43310546875,
    "net_worth": 1601

},

    {
        "player_slot": 5,
        "account_id": 91364275,
        "hero_id": 11,
        "kills": 4,
        "death": 4,
        "assists": 2,
        "last_hits": 165,
        "denies": 6,
        "gold": 1382,
        "level": 14,
        "gold_per_min": 524,
        "xp_per_min": 545,
        "ultimate_state": 3,
        "ultimate_cooldown": 0,
        "item0": 1,
        "item1": 41,
        "item2": 63,
        "item3": 100,
        "item4": 46,
        "item5": 21,
        "respawn_timer": 0,
        "position_x": -3362.665771484375,
        "position_y": 5149.03125,
        "net_worth": 9682
    }

],
"abilities":
[

{

    "ability_id": 5059,
    "ability_level": 4

},
{

    "ability_id": 5060,
    "ability_level": 4

},
{

    "ability_id": 5061,
    "ability_level": 4

},
{

    "ability_id": 5062,
    "ability_level": 4

},
{

    "ability_id": 5063,
    "ability_level": 4

},

                            {
                                "ability_id": 5064,
                                "ability_level": 2
                            }
                        ]
                    }
                }
            }
        ],
        "status": 200
    }

}"""
good_live_games = json.loads(live_strng)
