from django.test import TestCase
from teams.json_data import team_winrate_json
from matches.mommy_recipes import make_matchset
from model_mommy import mommy
from teams.models import Team
from django.utils import timezone
from datetime import timedelta


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


class TestModelMethods(TestCase):

    def setUp(self):
        self.team = mommy.make_recipe('teams.team')

    def test_update_save(self):
        self.team.save()
        self.assertLess(
            timezone.now()-self.team.update_time,
            timedelta(seconds=.1)
        )

    def test_outdated(self):
        self.team.update_time = timezone.now() - timedelta(weeks=10)
        self.team.valve_cdn_image = None
        self.assertEqual(self.team.is_outdated, True)

        self.team.update_time = timezone.now() - timedelta(weeks=10)
        self.team.valve_cdn_image = 'http://www.whatever.com/test.png'
        self.assertEqual(self.team.is_outdated, False)

        self.team.update_time = timezone.now()
        self.team.valve_cdn_image = None
        self.assertEqual(self.team.is_outdated, False)

        self.team.update_time = timezone.now()
        self.team.valve_cdn_image = 'http://www.whatever.com/test.png'
        self.assertEqual(self.team.is_outdated, False)
