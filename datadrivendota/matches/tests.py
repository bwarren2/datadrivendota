"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from .r import EndgameChart, MatchParameterScatterplot
from players.test_mixins import PlayerValidityMixin
from matches.test_mixins import MatchValidityMixin


# MIXINS
# TESTS
class EndgameChartTestCase(PlayerValidityMixin, MatchValidityMixin, TestCase):
    fixtures = [
        'datadrivendota/heroes/test_data.json',
        'datadrivendota/matches/test_data.json'
    ]

    def setUp(self):
        super(EndgameChartTestCase, self).setUp()

    def test_valid_call(self):
        foo = EndgameChart(
            player_list=self.valid_player_list,
            mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            split_var=self.valid_cat_var,
            group_var=self.valid_cat_var)
        self.assertNotEqual(foo.name, 'failface.png')

    def test_invalid_player(self):
        foo = EndgameChart(
            player_list=self.invalid_player_list,
            mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            split_var=self.valid_cat_var,
            group_var=self.valid_cat_var)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_modes(self):
        foo = EndgameChart(
            player_list=self.valid_player_list,
            mode_list=self.invalid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            split_var=self.valid_cat_var,
            group_var=self.valid_cat_var)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_x_var(self):
        foo = EndgameChart(
            player_list=self.valid_player_list,
            mode_list=self.valid_game_modes,
            x_var=self.invalid_x_var,
            y_var=self.valid_y_var,
            split_var=self.valid_cat_var,
            group_var=self.valid_cat_var)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_y_var(self):
        foo = EndgameChart(
            player_list=self.valid_player_list,
            mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.invalid_y_var,
            split_var=self.valid_cat_var,
            group_var=self.valid_cat_var)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_split_var(self):
        foo = EndgameChart(
            player_list=self.valid_player_list,
            mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            split_var=self.invalid_cat_var,
            group_var=self.valid_cat_var)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_group_var(self):
        foo = EndgameChart(
            player_list=self.valid_player_list,
            mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            split_var=self.valid_cat_var,
            group_var=self.invalid_cat_var)
        self.assertEqual(foo.name, 'failface.png')


class MatchParameterScatterplotTestCase(
        PlayerValidityMixin,
        MatchValidityMixin,
        TestCase
        ):
    fixtures = [
        'datadrivendota/heroes/test_data.json',
        'datadrivendota/matches/test_data.json'
    ]

    def setUp(self):
        super(MatchParameterScatterplotTestCase, self).setUp()

    def test_valid_call(self):
        foo = MatchParameterScatterplot(
            match_id=self.valid_match,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var)
        self.assertNotEqual(foo.name, 'failface.png')

    def test_invalid_match(self):
        foo = MatchParameterScatterplot(
            match_id=self.invalid_match,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_x_var(self):
        foo = MatchParameterScatterplot(
            match_id=self.invalid_match,
            x_var=self.invalid_x_var,
            y_var=self.valid_y_var)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_y_var(self):
        foo = MatchParameterScatterplot(
            match_id=self.invalid_match,
            x_var=self.valid_x_var,
            y_var=self.invalid_y_var)
        self.assertEqual(foo.name, 'failface.png')
