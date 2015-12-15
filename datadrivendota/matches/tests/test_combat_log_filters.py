from matches.management import combat_log_filters
from unittest import TestCase
import json
from model_mommy import mommy


class TestCombatlogFilters(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.msgs = json.loads(combatlog_json_strng)
        match = mommy.make_recipe('matches.match')
        cls.antimage_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_antimage',
            player_slot=1,
            match=match,
        )
        cls.axe_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_axe',
            player_slot=2,
            match=match,
        )
        cls.slardar_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_slardar',
            player_slot=128,
            match=match,
        )
        cls.rubick_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_rubick',
            player_slot=129,
            match=match,
        )
        cls.allies = cls.antimage_pms.allies
        cls.enemies = cls.antimage_pms.enemies

    def test_construct_integrity(self):
        """ Making sure the assumptions of setup are right """
        self.assertEqual(self.allies, [
            'npc_dota_hero_antimage', 'npc_dota_hero_axe'
        ])
        self.assertEqual(self.enemies, [
            'npc_dota_hero_rubick', 'npc_dota_hero_slardar'
        ])

    def test_combatlog_kills(self):
        data = combat_log_filters.kills(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['hero_kills'])

    def test_combatlog_deaths(self):
        data = combat_log_filters.deaths(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['hero_deaths'])

    def test_combatlog_lasthits(self):
        data = combat_log_filters.last_hits(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['creep_kills'])

    def test_combatlog_xp(self):
        data = combat_log_filters.xp(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 4)

    def test_combatlog_heal(self):
        data = combat_log_filters.healing(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['healing'])

    def test_combatlog_hero_damage_taken(self):
        data = combat_log_filters.hero_dmg_taken(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['hero_damage_taken'])

    def test_combatlog_hero_damage_dealt(self):
        data = combat_log_filters.hero_dmg_dealt(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['hero_damage_dealt'])

    def test_combatlog_other_damage_taken(self):
        data = combat_log_filters.other_dmg_taken(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['other_damage_taken'])

    def test_combatlog_other_damage_dealt(self):
        data = combat_log_filters.other_dmg_dealt(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['other_damage_dealt'])

    def test_combatlog_all_income(self):
        data = combat_log_filters.all_income(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        # This one is complicated because it returns all the gold entries.
        self.assertEqual(len(data), 11)
        # self.assertDictEqual(data[0], self.msgs['all_income'])

    def test_combatlog_earned_income(self):
        data = combat_log_filters.earned_income(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        # This one is complicated because it returns several gold entries.
        self.assertEqual(len(data), 10)
        # self.assertDictEqual(data[0], self.msgs['earned_income'])

    def test_combatlog_building_income(self):
        data = combat_log_filters.building_income(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['building_income'])

    def test_combatlog_courier_kill_income(self):
        data = combat_log_filters.courier_kill_income(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['courier_kill_income'])

    def test_combatlog_creep_kill_income(self):
        data = combat_log_filters.creep_kill_income(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], self.msgs['creep_kill_income'])

    def test_combatlog_hero_kill_income(self):
        data = combat_log_filters.hero_kill_income(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['hero_kill_income'])

    def test_combatlog_roshan_kill_income(self):
        data = combat_log_filters.roshan_kill_income(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['roshan_kill_income'])

    def test_combatlog_buyback_expense(self):
        data = combat_log_filters.buyback_expense(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['buyback_expense'])

    def test_combatlog_death_expense(self):
        data = combat_log_filters.death_expense(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['death_expense'])

    def test_combatlog_hero_xp(self):
        data = combat_log_filters.hero_xp(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['hero_xp'])

    def test_combatlog_creep_xp(self):
        data = combat_log_filters.creep_xp(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['creep_xp'])

    def test_combatlog_roshan_xp(self):
        data = combat_log_filters.roshan_xp(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['roshan_xp'])

    def test_combatlog_key_bldg_dmg_dealt(self):
        data = combat_log_filters.key_bldg_dmg_dealt(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['key_bldg_dmg_dealt'])

    def test_combatlog_key_bldg_kills(self):
        data = combat_log_filters.key_bldg_kills(
            self.msgs.values(),
            self.antimage_pms,
            self.enemies,
            self.allies,
        )
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], self.msgs['key_bldg_kills'])


combatlog_json_strng = """
{
  "xp_reasons": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 15,
    "attacker_illusion": false,
    "key": "0",
    "time": 3046,
    "y": 3689.094,
    "x": 4083.6072,
    "type": "xp_reasons"
  },
  "roshan_xp": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 15,
    "attacker_illusion": false,
    "key": "3",
    "time": 3046,
    "y": 3689.094,
    "x": 4083.6072,
    "type": "xp_reasons"
  },
  "hero_xp": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 15,
    "attacker_illusion": false,
    "key": "1",
    "time": 3046,
    "y": 3689.094,
    "x": 4083.6072,
    "type": "xp_reasons"
  },
  "creep_xp": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 15,
    "attacker_illusion": false,
    "key": "2",
    "time": 3046,
    "y": 3689.094,
    "x": 4083.6072,
    "type": "xp_reasons"
  },
  "purchase": {
    "target": "npc_dota_hero_bounty_hunter",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "attacker_illusion": false,
    "key": "item_guardian_greaves",
    "time": 3004,
    "y": 0.0,
    "x": 0.0,
    "type": "purchase"
  },
  "first_blood": {
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "attacker_illusion": false,
    "time": 1208,
    "y": 0.0,
    "x": 0.0,
    "type": "first_blood"
  },
  "ability_uses": {
    "attacker_illusion": false,
    "target_illusion": false,
    "attacker_hero": true,
    "target_hero": false,
    "inflictor": "antimage_blink",
    "attacker_name": "npc_dota_hero_antimage",
    "time": 3036,
    "y": 0.0,
    "x": 0.0,
    "type": "ability_uses"
  },
  "hero_kills": {
    "attacker_hero": true,
    "attacker_illusion": false,
    "attacker_name": "npc_dota_hero_antimage",
    "attacker_source": "npc_dota_hero_antimage",
    "target": "npc_dota_hero_slardar",
    "target_hero": true,
    "target_illusion": false,
    "target_source": "npc_dota_hero_slardar",
    "time": 3046,
    "type": "kills",
    "x": 0.0,
    "y": 0.0
  },
  "hero_deaths": {
    "attacker_hero": true,
    "attacker_illusion": false,
    "attacker_name": "npc_dota_hero_slardar",
    "attacker_source": "npc_dota_hero_slardar",
    "target": "npc_dota_hero_antimage",
    "target_hero": true,
    "target_illusion": false,
    "target_source": "npc_dota_hero_antimage",
    "time": 3046,
    "type": "kills",
    "x": 0.0,
    "y": 0.0
  },
  "creep_kills": {
    "attacker_illusion": true,
    "target": "npc_dota_creep_badguys_melee",
    "target_illusion": false,
    "attacker_hero": true,
    "attacker_source": "npc_dota_hero_antimage",
    "target_hero": false,
    "attacker_name": "npc_dota_hero_antimage",
    "y": 0.0,
    "time": 3046,
    "target_source": "npc_dota_creep_badguys_melee",
    "x": 0.0,
    "type": "kills"
  },
  "multi_kills": {
    "attacker_illusion": false,
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "attacker_name": "npc_dota_hero_antimage",
    "y": 0.0,
    "key": "3",
    "time": 3025,
    "target_source": "npc_dota_hero_slardar",
    "x": 0.0,
    "type": "multi_kills"
  },
  "hero_damage_taken": {
    "attacker_illusion": false,
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": true,
    "attacker_source": "npc_dota_hero_slardar",
    "target_hero": true,
    "value": 92,
    "attacker_name": "npc_dota_hero_slardar",
    "y": 0.0,
    "time": 3050,
    "target_source": "npc_dota_hero_antimage",
    "x": 0.0,
    "type": "damage"
  },
  "hero_damage_dealt": {
    "attacker_illusion": false,
    "target": "npc_dota_hero_slardar",
    "target_illusion": false,
    "attacker_hero": true,
    "attacker_source": "npc_dota_hero_antimage",
    "target_hero": true,
    "value": 92,
    "attacker_name": "npc_dota_hero_antimage",
    "y": 0.0,
    "time": 3050,
    "target_source": "npc_dota_hero_slardar",
    "x": 0.0,
    "type": "damage"
  },
  "other_damage_taken": {
    "attacker_illusion": false,
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": true,
    "attacker_source": "npc_dota_creep_badguys_ranged",
    "target_hero": true,
    "value": 92,
    "attacker_name": "npc_dota_creep_badguys_ranged",
    "y": 0.0,
    "time": 3050,
    "target_source": "npc_dota_hero_antimage",
    "x": 0.0,
    "type": "damage"
  },
  "other_damage_dealt": {
    "attacker_illusion": false,
    "target": "npc_dota_creep_badguys_ranged",
    "target_illusion": false,
    "attacker_hero": true,
    "attacker_source": "npc_dota_hero_antimage",
    "target_hero": true,
    "value": 92,
    "attacker_name": "npc_dota_hero_antimage",
    "y": 0.0,
    "time": 3050,
    "target_source": "npc_dota_creep_badguys_ranged",
    "x": 0.0,
    "type": "damage"
  },

  "key_bldg_dmg_dealt": {
    "attacker_illusion": false,
    "target": "npc_dota_badguys_range_rax_mid",
    "target_illusion": false,
    "attacker_hero": true,
    "attacker_source": "npc_dota_hero_antimage",
    "target_hero": false,
    "value": 92,
    "attacker_name": "npc_dota_hero_antimage",
    "y": 0.0,
    "time": 3050,
    "target_source": "npc_dota_badguys_range_rax_mid",
    "x": 0.0,
    "type": "damage"
  },
  "key_bldg_kills": {
    "attacker_hero": true,
    "attacker_illusion": false,
    "attacker_name": "npc_dota_hero_antimage",
    "attacker_source": "npc_dota_hero_antimage",
    "target": "npc_dota_badguys_range_rax_mid",
    "target_hero": true,
    "target_illusion": false,
    "target_source": "npc_dota_badguys_range_rax_mid",
    "time": 3046,
    "type": "kills",
    "x": 0.0,
    "y": 0.0
  },

  "gold_reasons": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "13",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "other_gold": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "0",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "death_expense": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "1",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "buyback_expense": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "2",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "abandon_income": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "5",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "sell_income": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "6",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "building_income": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "11",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "hero_kill_income": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "12",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "creep_kill_income": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "13",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "roshan_kill_income": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "14",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "courier_kill_income": {
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "value": 38,
    "attacker_illusion": false,
    "key": "15",
    "time": 3046,
    "y": 3627.92,
    "x": 4127.969,
    "type": "gold_reasons"
  },
  "state": {
    "type": "state",
    "value": 3050,
    "key": "POST_GAME",
    "time": 3050
  },
  "kill_streaks": {
    "attacker_illusion": false,
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "attacker_name": "npc_dota_hero_antimage",
    "y": 0.0,
    "key": "7",
    "time": 3025,
    "target_source": "npc_dota_hero_slardar",
    "x": 0.0,
    "type": "kill_streaks"
  },
  "healing": {
    "attacker_illusion": false,
    "target": "npc_dota_hero_antimage",
    "target_illusion": false,
    "attacker_hero": true,
    "attacker_source": "npc_dota_hero_antimage",
    "target_hero": true,
    "value": 36,
    "inflictor": "item_vladmir",
    "attacker_name": "npc_dota_hero_antimage",
    "y": 0.0,
    "time": 3046,
    "target_source": "npc_dota_hero_antimage",
    "x": 0.0,
    "type": "healing"
  },
  "item_uses": {
    "attacker_illusion": false,
    "target_illusion": false,
    "attacker_hero": true,
    "target_hero": false,
    "inflictor": "item_manta",
    "attacker_name": "npc_dota_hero_antimage",
    "time": 3036,
    "y": 0.0,
    "x": 0.0,
    "type": "item_uses"
  },
  "team_building_kill": {
    "target": "npc_dota_badguys_fort",
    "target_illusion": false,
    "attacker_hero": false,
    "target_hero": false,
    "attacker_illusion": false,
    "key": "3",
    "time": 3050,
    "y": 0.0,
    "x": 0.0,
    "type": "team_building_kill"
  }
}
"""
