from django.test import TestCase, Client
from model_mommy import mommy
from django.core.urlresolvers import reverse

from matches.viewsets import MatchPickBanViewSet
from matches.mommy_recipes import make_league_match
from matches.models import Match
from matches.management.tasks import filter_msgs


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUrlconf, cls).setUpClass()
        cls.match = mommy.make_recipe('matches.match')

    def test_url_ok(self):
        c = Client()

        resp = c.get(reverse('matches:index'))
        self.assertEqual(resp.status_code, 200)

        resp = c.get(
            reverse(
                'matches:detail',
                kwargs={'match_id': self.match.steam_id}
            )
        )
        self.assertEqual(resp.status_code, 200)

        resp = c.get(
            reverse(
                'matches:detail',
                kwargs={'match_id': -1}
            )
        )
        self.assertEqual(resp.status_code, 404)


class TestTrickyViewsets(TestCase):

    @classmethod
    def setUpClass(cls):

        super(TestTrickyViewsets, cls).setUpClass()
        make_league_match()

    def test_viewset_qs_values(self):
        matches = Match.objects.filter(
            game_mode__steam_id=2
        ).values('steam_id')
        pickban_qs = MatchPickBanViewSet()._get_pickban_queryset(matches)

        self.assertEqual(
            pickban_qs.count(),
            20
        )

        keyset = set([
            'pickban__order',
            'steam_id',
            'start_time',
            'pickban__team',
            'duration',
            'pickban__is_pick',
            'radiant_win',
            'pickban__hero__steam_id',
            'dire_team__name',
            'radiant_team__name',
        ])

        for x in pickban_qs:
            self.assertEqual(set(x.keys()), keyset)

    def test_viewset_qs_refactor(self):
        matches = Match.objects.filter(
            game_mode__steam_id=2
        ).values('steam_id')
        pickban_qs = MatchPickBanViewSet()._get_pickban_queryset(matches)
        out = MatchPickBanViewSet()._refactor_pickbans(pickban_qs)
        self.assertEqual(len(out), 1)

        self.assertEqual(len(out), 1)
        match_keyset = set([
            'radiant_win',
            'steam_id',
            'start_time',
            'pickbans',
            'radiant_team',
            'dire_team',
            'duration',
        ])
        self.assertEqual(set(out[0].keys()), match_keyset)
        self.assertEqual(len(out[0]['pickbans']), 20)

        pickban_keyset = set([
            'hero',
            'is_pick',
            'order',
            'team',
        ])

        hero_keyset = set([
            'steam_id',
        ])
        self.assertEqual(set(out[0]['pickbans'][0].keys()), pickban_keyset)
        self.assertEqual(
            set(out[0]['pickbans'][0]['hero'].keys()),
            hero_keyset
        )


class TestReplayFiltration(TestCase):

    def test_filter_fn(self):
        antimage_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_antimage',
            player_slot=1
        )
        rubick_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_rubick',
            player_slot=2
        )
        sample = {
            u'ability_uses': {
                u'key': u'rubick_fade_bolt',
                u'time': 2974,
                u'type': u'ability_uses',
                u'unit': u'npc_dota_hero_rubick'
            },
            u'buyback_log': {
                u'slot': 1, u'time': 2948, u'type': u'buyback_log'
            },
            u'damage': {
                u'key': u'npc_dota_hero_antimage (illusion)',
                u'target_hero': True,
                u'target_illusion': True,
                u'target_source': u'npc_dota_hero_antimage',
                u'time': 2978,
                u'type': u'damage',
                u'unit': u'npc_dota_creep_goodguys_ranged',
                u'value': 27},
            u'gold_reasons': {
                u'key': u'13',
                u'time': 2976,
                u'type': u'gold_reasons',
                u'unit': u'npc_dota_hero_lina',
                u'value': 14},
            u'healing': {
                u'key': u'npc_dota_hero_storm_spirit',
                u'time': 2979,
                u'type': u'healing',
                u'unit': u'npc_dota_hero_storm_spirit',
                u'value': 54
            },
            u'item_uses': {
                u'key': u'item_black_king_bar',
                u'time': 2977,
                u'type': u'item_uses',
                u'unit': u'npc_dota_hero_antimage'
            },
            u'kill_streaks': {
                u'key': u'6',
                u'time': 0,
                u'type': u'kill_streaks',
                u'unit': u'npc_dota_hero_lina'
            },
            u'kills': {
                u'key': u'npc_dota_neutral_mud_golem_split',
                u'target_hero': False,
                u'target_illusion': False,
                u'target_source': u'npc_dota_neutral_mud_golem_split',
                u'time': 2976,
                u'type': u'kills',
                u'unit': u'npc_dota_hero_lina'
            },
            u'modifier_applied': {
                u'key': u'modifier_invisible',
                u'time': 2981,
                u'type': u'modifier_applied',
                u'unit': u'npc_dota_hero_lina'
            },
            u'multi_kills': {
                u'key': u'3',
                u'time': 0,
                u'type': u'multi_kills',
                u'unit': u'npc_dota_hero_antimage'
            },
            u'purchase': {
                u'key': u'item_tpscroll',
                u'time': 2966,
                u'type': u'purchase',
                u'unit': u'npc_dota_hero_rubick'
            },
            u'state': {
                u'key': u'6', u'time': 3068, u'type': u'state', u'value': 3068
            },
            u'xp_reasons': {
                u'key': u'2',
                u'time': 2977,
                u'type': u'xp_reasons',
                u'unit': u'npc_dota_hero_rubick',
                u'value': 12
            }
        }
        self.assertEqual(
            filter_msgs(rubick_pms, sample['xp_reasons']),
            True
        )
        self.assertEqual(
            filter_msgs(antimage_pms, sample['xp_reasons']),
            False
        )
        self.assertEqual(
            filter_msgs(rubick_pms, sample['buyback_log']),
            False
        )
        self.assertEqual(
            filter_msgs(antimage_pms, sample['buyback_log']),
            True
        )
        self.assertEqual(
            filter_msgs(antimage_pms, sample['damage']),
            True
        )
        self.assertEqual(
            filter_msgs(rubick_pms, sample['damage']),
            False
        )
