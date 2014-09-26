from django.test import TestCase
from matches.mommy_recipes import make_matchset
from items.json_data import item_endgame


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
