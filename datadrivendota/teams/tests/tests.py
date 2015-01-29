from django.test import TestCase
from teams.json_data import team_winrate_json
from matches.mommy_recipes import make_matchset
# from model_mommy import mommy
from teams.models import Team


class TestWorkingJson(TestCase):

    def setUp(self):
        self.hero, self.player = make_matchset()
        self.team = Team.objects.get(steam_id=1333179)

    def tearDown(self):
        pass

    def test_team_winrate_json(self):
        chart = team_winrate_json(
            team=self.team.steam_id,
            game_modes=None,
            min_date=None,
            max_date=None,
            group_var='alignment',
        )
        self.assertGreater(len(chart.datalist), 0)
