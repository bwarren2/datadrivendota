"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

#from django.contrib.auth.models import User
#from django.test.client import Client
from django.test import TestCase
from .r import EndgameChart, MatchParameterScatterplot
from .models import Match
from players.tests import PlayerValidityMixin

#MIXINS
class MatchValidityMixin(object):
    def setUp(self):
        self.valid_x_var = 'duration'
        self.invalid_x_var = 'blicketude'
        self.valid_y_var='kills'
        self.invalid_y_var='snufflupagus'
        self.valid_cat_var='is_win'
        self.invalid_cat_var='chumbliness'
        self.valid_game_modes=[1,2,3]
        self.invalid_game_modes=[-1,-2]
        self.valid_match = Match.objects.all()[0].steam_id
        self.invalid_match = -1
        super(MatchValidityMixin,self).setUp()

#TESTS
class EndgameChartTestCase(PlayerValidityMixin, MatchValidityMixin, TestCase):
    fixtures = ['datadrivendota/matches/test_data.json']
    def setUp(self):
        super(EndgameChartTestCase,self).setUp()

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

class MatchParameterScatterplotTestCase(PlayerValidityMixin, MatchValidityMixin, TestCase):
    fixtures = ['datadrivendota/matches/test_data.json']
    def setUp(self):
        super(MatchParameterScatterplotTestCase,self).setUp()

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


