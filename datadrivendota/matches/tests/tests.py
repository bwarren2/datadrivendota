from nose.tools import timed
from django.test import TestCase

from matches.models import PlayerMatchSummary, Match, GameMode, SkillBuild
from matches.mommy_recipes import make_matchset
from matches.json_data import (
    player_team_endgame_json,
    player_endgame_json,
    team_endgame_json,
    match_ability_json,
    match_parameter_json,
    single_match_parameter_json,
    match_role_json,
    match_list_json,
    match_set_progression_json,
    )

JSON_TIME = .2

# test_team_endgame_json is using its own time and needs work.


class TestMommy(TestCase):

    def test_mommy(self):
        make_matchset()


class TestModel(TestCase):

    def setUp(self):
        rad_win_match = Match(steam_id=1, radiant_win=True)
        dire_win_match = Match(steam_id=1, radiant_win=False)
        self.rad_win = PlayerMatchSummary(
            match=rad_win_match,
            player_slot=0
            )
        self.dire_win = PlayerMatchSummary(
            match=dire_win_match,
            player_slot=132
            )
        self.rad_loss = PlayerMatchSummary(
            match=dire_win_match,
            player_slot=0
            )
        self.dire_loss = PlayerMatchSummary(
            match=rad_win_match,
            player_slot=132
            )

    def test_wins(self):
        self.assertEqual(self.rad_win.determine_win(), True)
        self.assertEqual(self.dire_win.determine_win(), True)
        self.assertEqual(self.rad_loss.determine_win(), False)
        self.assertEqual(self.dire_loss.determine_win(), False)

    def test_sides(self):
        self.assertEqual(self.rad_win.side, 'Radiant')
        self.assertEqual(self.dire_win.side, 'Dire')


class TestWorkingJson(TestCase):

    @classmethod
    def setUpClass(self):
        self.hero, self.player = make_matchset()
        self.player.updated = True
        sbs = SkillBuild.objects.all()
        self.match_id = sbs[0].player_match_summary.match.steam_id

    def tearDown(self):
        pass

    @timed(JSON_TIME)
    def test_player_team_endgame_json(self):
        chart = player_team_endgame_json(
            players=[self.player.steam_id],
            game_modes=[x.steam_id for x in GameMode.objects.all()],
            x_var='duration',
            y_var='kills',
            panel_var=None,
            group_var=None,
        )
        self.assertGreater(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_player_endgame_json(self):
        chart = player_endgame_json(
            players=[self.player.steam_id],
            game_modes=[x.steam_id for x in GameMode.objects.all()],
            x_var='duration',
            y_var='kills',
            panel_var=None,
            group_var=None,
        )
        self.assertGreater(len(chart.datalist), 1)

    @timed(1.5)
    def test_team_endgame_json(self):
        chart = team_endgame_json(
            players=[self.player.steam_id],
            game_modes=[x.steam_id for x in GameMode.objects.all()],
            x_var='duration',
            y_var='kills',
            panel_var=None,
            group_var=None,
            compressor=None,
        )
        self.assertGreater(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_match_ability_json(self):
        chart = match_ability_json(
            self.match_id,
            panel_var=None
        )
        self.assertGreater(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_match_parameter_json(self):
        chart = match_parameter_json(
            self.match_id,
            x_var='kills',
            y_var='deaths'
        )
        self.assertEqual(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_single_match_parameter_json(self):
        chart = single_match_parameter_json(self.match_id, y_var='kills')
        self.assertEqual(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_match_role_json(self):
        chart = match_role_json(self.match_id)
        self.assertEqual(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_match_list_json(self):
        chart = match_list_json(
            matches=[self.match_id],
            players=[self.player.steam_id]
            )
        self.assertGreater(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_match_set_progression_json(self):
        chart = match_set_progression_json(
            hero=self.hero.steam_id,
            match_set_1=[self.match_id],
            match_set_2=[self.match_id],
            match_set_3=[self.match_id],
            )
        self.assertGreater(len(chart.datalist), 1)
