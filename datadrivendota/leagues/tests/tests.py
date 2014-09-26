from django.test import TestCase
from leagues.json_data import league_winrate_json
from leagues.models import League
from matches.mommy_recipes import make_matchset


class TestWorkingJson(TestCase):

    def setUp(self):
        make_matchset()
        self.league = League.objects.all()[0]

    def tearDown(self):
        pass

    def test_winrate_json(self):
        chart = league_winrate_json(
            league=self.league.steam_id,
            min_date=None,
            max_date=None,
            group_var='alignment',
        )
        self.assertGreater(len(chart.datalist), 0)
