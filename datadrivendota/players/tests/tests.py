from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from model_mommy import mommy
from matches.mommy_recipes import make_matchset
from players.json_data import (
    player_winrate_json,
    player_hero_abilities_json,
    player_versus_winrate_json,
    player_role_json,
)


class TestMommy(TestCase):

    def test_mommy(self):
        mommy.make_recipe('players.player')


class TestWorkingJson(TestCase):

    @classmethod
    def setUpClass(self):
        super(TestWorkingJson, self).setUpClass()
        self.hero, self.player = make_matchset()
        self.hero_2, self.player_2 = make_matchset()

    def tearDown(self):
        pass

    def test_winrate_json(self):
        chart = player_winrate_json(
            player=self.player.steam_id,
            game_modes=None,
            role_list=[],
            min_date=None,
            max_date=None,
            group_var='alignment',
        )
        self.assertGreater(len(chart.datalist), 0)

    def test_player_hero_abilities_json(self):
        chart = player_hero_abilities_json(
            player_1=self.player.steam_id,
            hero_1=self.hero.steam_id,
            player_2=None,
            hero_2=None,
            game_modes=None,
            division=None
        )
        self.assertGreater(len(chart.datalist), 0)

    def test_player_versus_winrate_json(self):
        chart = player_versus_winrate_json(
            player_1=self.player.steam_id,
            player_2=self.player_2.steam_id,
            game_modes=None,
            min_date=None,
            max_date=None,
            group_var='alignment',
            plot_var='winrate',
        )
        self.assertGreater(len(chart.datalist), 0)

    def test_player_hero_side_json(self):
        pass
        # Requires more mommy work, which requires profiling
        # chart = player_hero_side_json(
        #     player=self.player.steam_id,
        #     group_var='alignment',
        #     plot_var='winrate',
        # )
        # self.assertGreater(len(chart.datalist), 0)

    def test_player_role_json(self):
        chart = player_role_json(
            player_1=self.player.steam_id,
            player_2=None,
            plot_var='performance',
        )
        self.assertGreater(len(chart.datalist), 0)


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(self):
        super(TestUrlconf, self).setUpClass()
        self.player = mommy.make_recipe('players.player')

    def test_url_ok(self):
        c = Client()

        resp = c.get('/players/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/players/all-players/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/players/{0}/'.format(self.player.steam_id))
        self.assertEqual(resp.status_code, 200)

    def test_url_login(self):
        c = Client()
        resp = c.get('/players/followed/')
        self.assertEqual(resp.status_code, 302)
        # We need to refactor the permissions conventions as well.
        # Test success later.
