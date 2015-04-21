from django.test import TestCase, Client
from matches.mommy_recipes import make_matchset
from items.json_data import item_endgame
from model_mommy import mommy


class TestWorkingJson(TestCase):

    def setUp(self):
        self.hero, self.player = make_matchset()

    def tearDown(self):
        pass

    def test_item_endgame_json(self):
        chart = item_endgame(
            hero=self.hero.steam_id,
            player=self.player.steam_id,
            skill_level=None,
            game_modes=[],
        )
        self.assertGreater(len(chart.datalist), 0)


class TestUrlconf(TestCase):

    def setUp(self):
        self.item = mommy.make_recipe(
            'items.item', slug_name='dagon', cost=1
        )

    def test_urls_ok(self):
        c = Client()

        resp = c.get('/items/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/items/dagon/')
        self.assertEqual(resp.status_code, 200)
