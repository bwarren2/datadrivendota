from parserpipe.management import state_log_filters
from unittest import TestCase
import json
from model_mommy import mommy


class TestStateLogFilters(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.msgs = json.loads(state_log_json_strng)
        match = mommy.make_recipe('matches.match')
        cls.antimage_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_windrunner',
            hero__steam_id=21,
            player_slot=1,
            match=match,
        )

    def test_state_log_agility(self):
        data = state_log_filters.agility(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {"offset_time": 276, "agility": 19.8},
            {"offset_time": 1166, "agility": 26.799997}
        ])

    def test_state_log_agility_total(self):
        data = state_log_filters.agility_total(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "agility_total": 20.8},
            {'offset_time': 1166, "agility_total": 30.799997}
        ])

    def test_state_log_strength(self):
        data = state_log_filters.strength(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "strength": 20.0},
            {'offset_time': 1166, "strength": 32.5}
        ])

    def test_state_log_strength_total(self):
        data = state_log_filters.strength_total(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "strength_total": 21.0},
            {'offset_time': 1166, "strength_total": 36.5}
        ])

    def test_state_log_intelligence(self):
        data = state_log_filters.intelligence(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "intelligence": 27.2},
            {'offset_time': 1166, "intelligence": 40.199997}
        ])

    def test_state_log_intelligence_total(self):
        data = state_log_filters.intelligence_total(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "intelligence_total": 28.2},
            {'offset_time': 1166, "intelligence_total": 44.199997}
        ])

    def test_state_log_base_damage(self):
        data = state_log_filters.base_damage(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
              'base_damage': 56,
              'offset_time': 276,
            },
            {
              'base_damage': 72,
              'offset_time': 1166,
            }
          ])

    def test_state_log_bonus_damage(self):
        data = state_log_filters.bonus_damage(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
              'bonus_damage': 0,
              'offset_time': 276,
            },
            {
              'bonus_damage': 0,
              'offset_time': 1166,
            }
          ])

    def test_state_log_total_damage(self):
        data = state_log_filters.total_damage(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
              'offset_time': 276,
              'total_damage': 56
            },
            {
              'offset_time': 1166,
              'total_damage': 72
            }
          ])

    def test_state_log_damage_taken(self):
        data = state_log_filters.damage_taken(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "damage_taken": 0},
            {'offset_time': 1166, "damage_taken": 0}
        ])

    def test_state_log_healing(self):
        data = state_log_filters.healing(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "healing": 0},
            {'offset_time': 1166, "healing": 0}
        ])

    def test_state_log_health(self):
        data = state_log_filters.health(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
                'offset_time': 276,
                "health": 549,
            },
            {
                'offset_time': 1166,
                "health": 834,
            }
        ])

    def test_state_log_max_health(self):
        data = state_log_filters.max_health(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
                'offset_time': 276,
                "max_health": 549
            },
            {
                'offset_time': 1166,
                "max_health": 834,
            }
        ])

    def test_state_log_pct_health(self):
        data = state_log_filters.pct_health(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
                'offset_time': 276,
                "pct_health": 1
            },
            {
                'offset_time': 1166,
                "pct_health": 1,
            }
        ])

    def test_state_log_mana(self):
        data = state_log_filters.mana(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
                'offset_time': 276,
                "mana": 206.0002,
            },
            {
                'offset_time': 1166,
                "mana": 771.87573,
            }
        ])

    def test_state_log_max_mana(self):
        data = state_log_filters.max_mana(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
                'offset_time': 276,
                "max_mana": 363.93784
            },
            {
                'offset_time': 1166,
                "max_mana": 821.9383,
            }
        ])

    def test_state_log_pct_mana(self):
        data = state_log_filters.pct_mana(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
                'offset_time': 276,
                "pct_mana": 206.0002/363.93784
            },
            {
                'offset_time': 1166,
                "pct_mana": 771.87573/821.9383,
            }
        ])

    def test_state_log_kills(self):
        data = state_log_filters.kills(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "kills": 0},
            {'offset_time': 1166, "kills": 2}
        ])

    def test_state_log_deaths(self):
        data = state_log_filters.deaths(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "deaths": 0},
            {'offset_time': 1166, "deaths": 5}
        ])

    def test_state_log_assists(self):
        data = state_log_filters.assists(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "assists": 0},
            {'offset_time': 1166, "assists": 0}
        ])

    def test_state_log_items(self):
        data = state_log_filters.items(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {
                'offset_time': 276,
                "item_0": None,
                "item_1": None,
                "item_2": 342,
                "item_3": 338,
                "item_4": 343,
                "item_5": None,
            },
            {
                'offset_time': 1166,
                "item_0": 389,
                "item_1": 330,
                "item_2": 385,
                "item_3": 370,
                "item_4": 378,
                "item_5": None,
            }
        ])

    def test_state_log_last_hits(self):
        data = state_log_filters.last_hits(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "last_hits": 3},
            {'offset_time': 1166, "last_hits": 11}
        ])

    def test_state_log_denies(self):
        data = state_log_filters.denies(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "denies": 2},
            {'offset_time': 1166, "denies": 5}
        ])

    def test_state_log_misses(self):
        data = state_log_filters.misses(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "misses": 6},
            {'offset_time': 1166, "misses": 11}
        ])

    def test_state_log_lifestate(self):
        data = state_log_filters.lifestate(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "lifestate": 0},
            {'offset_time': 1166, "lifestate": 0}
        ])

    def test_state_log_magic_resist_pct(self):
        data = state_log_filters.magic_resist_pct(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "magic_resist_pct": 25.0},
            {'offset_time': 1166, "magic_resist_pct": 25.0}
        ])

    def test_state_log_armor(self):
        data = state_log_filters.armor(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "armor": -1.0},
            {'offset_time': 1166, "armor": -1.0}
        ])

    def test_state_log_recent_damage(self):
        data = state_log_filters.recent_damage(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "recent_damage": 0},
            {'offset_time': 1166, "recent_damage": 0}
        ])

    def test_state_log_respawn_time(self):
        data = state_log_filters.respawn_time(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "respawn_time": 0},
            {'offset_time': 1166, "respawn_time": -1.0}
        ])

    def test_state_log_roshan_kills(self):
        data = state_log_filters.roshan_kills(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "roshan_kills": 0},
            {'offset_time': 1166, "roshan_kills": 0}
        ])

    def test_state_log_nearby_creep_deaths(self):
        data = state_log_filters.nearby_creep_deaths(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "nearby_creep_deaths": 27},
            {'offset_time': 1166, "nearby_creep_deaths": 91}
        ])

    def test_state_log_shared_gold(self):
        data = state_log_filters.shared_gold(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "shared_gold": 0},
            {'offset_time': 1166, "shared_gold": 325}
        ])

    def test_state_log_reliable_gold(self):
        data = state_log_filters.reliable_gold(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "reliable_gold": 0},
            {'offset_time': 1166, "reliable_gold": 543}
        ])

    def test_state_log_total_earned_gold(self):
        data = state_log_filters.total_earned_gold(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "total_earned_gold": 690},
            {'offset_time': 1166, "total_earned_gold": 4301}
        ])

    def test_state_log_unreliable_gold(self):
        data = state_log_filters.unreliable_gold(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "unreliable_gold": 240},
            {'offset_time': 1166, "unreliable_gold": 33}
        ])

    def test_state_log_creep_kill_gold(self):
        data = state_log_filters.creep_kill_gold(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "creep_kill_gold": 82},
            {'offset_time': 1166, "creep_kill_gold": 412}
        ])

    def test_state_log_hero_kill_gold(self):
        data = state_log_filters.hero_kill_gold(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "hero_kill_gold": 0},
            {'offset_time': 1166, "hero_kill_gold": 953}
        ])

    def test_state_log_income_gold(self):
        data = state_log_filters.income_gold(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "income_gold": 608},
            {'offset_time': 1166, "income_gold": 2091}
        ])

    def test_state_log_tower_kills(self):
        data = state_log_filters.tower_kills(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "tower_kills": 0},
            {'offset_time': 1166, "tower_kills": 0}
        ])

    def test_state_log_xp(self):
        data = state_log_filters.xp(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "xp": 801},
            {'offset_time': 1166, "xp": 3208}
        ])

    def test_state_log_position(self):
        data = state_log_filters.position(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "x": 132, "y": 132},
            {'offset_time': 1166, "x": 154, "y": 154}
        ])

    def test_state_log_x_position(self):
        data = state_log_filters.x_position(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "x_position": 132},
            {'offset_time': 1166, "x_position": 154}
        ])

    def test_state_log_y_position(self):
        data = state_log_filters.y_position(
            self.msgs, self.antimage_pms
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data, [
            {'offset_time': 276, "y_position": 132},
            {'offset_time': 1166, "y_position": 154}
        ])


state_log_json_strng = """
    [{
      "agility": 26.799997,
      "agility_total": 30.799997,
      "armor": -1.0,
      "assists": 0,
      "creep_kill_gold": 412,
      "damage_bonus": 0,
      "damage_max": 78,
      "damage_min": 66,
      "damage_taken": 0,
      "deaths": 5,
      "denies": 5,
      "healing": 0.0,
      "health": 834,
      "hero_id": 21,
      "hero_kill_gold": 953,
      "income_gold": 2091,
      "intelligence": 40.199997,
      "intelligence_total": 44.199997,
      "kills": 2,
      "last_hits": 11,
      "lifestate": 0,
      "magic_resist_pct": 25.0,
      "mana": 771.87573,
      "max_health": 834,
      "max_mana": 821.9383,
      "misses": 11,
      "nearby_creep_deaths": 91,
      "offset_time": 1166,
      "player_slot": 9,
      "recent_damage": 0,
      "reliable_gold": 543,
      "respawn_time": -1.0,
      "roshan_kills": 0,
      "shared_gold": 325,
      "strength": 32.5,
      "strength_total": 36.5,
      "tick_time": 2166,
      "total_earned_gold": 4301,
      "tower_kills": 0,
      "unreliable_gold": 33,
      "x": 154,
      "xp": 3208,
      "y": 154,
      "item_0": 389,
      "item_1": 330,
      "item_2": 385,
      "item_3": 370,
      "item_4": 378,
      "item_5": null
    },
    {
      "agility": 19.8,
      "agility_total": 20.8,
      "armor": -1.0,
      "assists": 0,
      "creep_kill_gold": 82,
      "damage_bonus": 0,
      "damage_max": 62,
      "damage_min": 50,
      "damage_taken": 0,
      "deaths": 0,
      "denies": 2,
      "healing": 0.0,
      "health": 549,
      "hero_id": 21,
      "hero_kill_gold": 0,
      "income_gold": 608,
      "intelligence": 27.2,
      "intelligence_total": 28.2,
      "item_0": 362,
      "kills": 0,
      "last_hits": 3,
      "lifestate": 0,
      "magic_resist_pct": 25.0,
      "mana": 206.0002,
      "max_health": 549,
      "max_mana": 363.93784,
      "misses": 6,
      "nearby_creep_deaths": 27,
      "offset_time": 276,
      "player_slot": 9,
      "recent_damage": 0,
      "reliable_gold": 0,
      "respawn_time": 0.0,
      "roshan_kills": 0,
      "shared_gold": 0,
      "strength": 20.0,
      "strength_total": 21.0,
      "tick_time": 1276,
      "total_earned_gold": 690,
      "tower_kills": 0,
      "unreliable_gold": 240,
      "x": 132,
      "xp": 801,
      "y": 132,
      "item_0": null,
      "item_1": null,
      "item_2": 342,
      "item_3": 338,
      "item_4": 343,
      "item_5": null
    }]
"""
