from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings

from model_mommy import mommy

from datadrivendota.management.tasks import ApiContext

from matches.viewsets import MatchPickBanViewSet
from matches.mommy_recipes import make_league_match
from matches.models import Match, PickBan, PlayerMatchSummary

from matches.tests import json_samples
from matches.management.tasks import UpdateMatch

from players.models import Player
from items.models import Item


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


class TestModelMethods(TestCase):

    def test_adversaries(self):
        match = mommy.make_recipe(
            'matches.match',
        )

        mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_antimage',
            player_slot=1,
            match=match
        )
        axe_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_axe',
            player_slot=2,
            match=match
        )
        mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_rubick',
            player_slot=128,
            match=match
        )
        juggernaut_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            hero__internal_name='npc_dota_hero_juggernaut',
            player_slot=129,
            match=match
        )
        self.assertEqual(
            juggernaut_pms.allies,
            [u'npc_dota_hero_juggernaut', u'npc_dota_hero_rubick']
        )
        self.assertEqual(
            axe_pms.allies,
            [u'npc_dota_hero_antimage', u'npc_dota_hero_axe']
        )
        self.assertEqual(
            juggernaut_pms.enemies,
            [u'npc_dota_hero_antimage', u'npc_dota_hero_axe']
        )
        self.assertEqual(
            axe_pms.enemies,
            [u'npc_dota_hero_juggernaut', u'npc_dota_hero_rubick']
        )


class TestMatchUpload(TestCase):

    def test_run(self):
        api_context = ApiContext()
        api_context.match_id = 1906861533

        UpdateMatch().run(
            api_context,
            json_samples.valid_match,
            200,
            "test"
        )

        self.assertEqual(Match.objects.all().count(), 1)
        self.assertEqual(PickBan.objects.all().count(), 20)
        self.assertEqual(Player.objects.all().count(), 11)
        self.assertEqual(Item.objects.all().count(), 35)
        self.assertEqual(PlayerMatchSummary.objects.all().count(), 10)


class TestMatchNotFound(TestCase):

    def test_run(self):
        api_context = ApiContext()
        api_context.match_id = 1795416549

        UpdateMatch().run(
            api_context,
            json_samples.not_found_match,
            200,
            "test"
        )

        self.assertEqual(Match.objects.all().count(), 0)


class TestEmptyMatch(TestCase):

    def test_run(self):
        api_context = ApiContext()
        api_context.match_id = 1795416549

        UpdateMatch().run(
            api_context,
            json_samples.empty_match,
            200,
            "test"
        )

        self.assertEqual(Match.objects.all().count(), 0)


class TestMatchManagers(TestCase):

    @classmethod
    def setUpClass(cls):

        super(TestMatchManagers, cls).setUpClass()
        cls.unparsed_match = mommy.make_recipe(
            'matches.match', parsed_with=None
        )
        cls.parsed_match = mommy.make_recipe(
            'matches.match', parsed_with=settings.PARSER_VERSION
        )

    def test_unparsed(self):

        self.assertQuerysetEqual(
            Match.unparsed.all(),
            map(repr, Match.objects.filter(id=self.unparsed_match.id))
        )  # Because aQsE compares reprs.

    def test_parsed(self):

        self.assertQuerysetEqual(
            Match.parsed.all(),
            map(repr, Match.objects.filter(id=self.parsed_match.id))
        )  # Because aQsE compares reprs.
