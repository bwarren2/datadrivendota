"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from matches.models import PlayerMatchSummary
from .r import KDADensity, CountWinrate
from matches.tests import MatchValidityMixin
import datetime
###MIXINS
class PlayerValidityMixin(object):
    def setUp(self):
        self.valid_player = PlayerMatchSummary.objects.all()[0].player.steam_id
        self.invalid_player = -1
        self.valid_player_list = [pms.player.steam_id for pms in PlayerMatchSummary.objects.all()[0:3]]
        self.invalid_player_list = []
        super(PlayerValidityMixin,self).setUp()

###TESTS
class KDADensityTestCase(PlayerValidityMixin, MatchValidityMixin, TestCase):
    fixtures = ['datadrivendota/matches/test_data.json']
    def setUp(self):
        super(KDADensityTestCase,self).setUp()

    def test_valid_call(self):
        foo = KDADensity(self.valid_player)
        self.assertNotEqual(foo.name, 'failface.png')

    def test_invalid_call(self):
        foo = KDADensity(self.invalid_player)
        self.assertEqual(foo.name, 'failface.png')

class CountWinrateTestCase(PlayerValidityMixin, TestCase):
    fixtures = ['datadrivendota/matches/test_data.json']
    def setUp(self):
        super(CountWinrateTestCase,self).setUp()

    def test_valid_call_defaults(self):
        foo = CountWinrate(player_id=self.valid_player)
        self.assertNotEqual(foo.name, 'failface.png')

    def test_valid_call(self):
        foo = CountWinrate(player_id=self.valid_player,
            game_mode_list=self.valid_game_modes,
            min_date=datetime.date(2009,1,1),
            max_date="2012-03-01")
        self.assertNotEqual(foo.name, 'failface.png')

    def test_invalid_players(self):
        foo = CountWinrate(player_id=self.invalid_player,
            game_mode_list=self.valid_game_modes,
)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_modes(self):
        foo = CountWinrate(player_id=self.valid_player,
            game_mode_list=self.invalid_game_modes)
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_date_order(self):
        foo = CountWinrate(player_id=self.valid_player,
            game_mode_list=self.valid_game_modes,
            min_date="2012-01-01",
            max_date="2010-03-01")
        self.assertEqual(foo.name, 'failface.png')

class PlayerTimeline(PlayerValidityMixin, TestCase):
    fixtures = ['datadrivendota/matches/test_data.json']
    def setUp(self):
        super(PlayerTimeline,self).setUp()

    def test_valid_call_defaults(self):
        foo = PlayerTimeline(player_id, min_date, max_date, bucket_var, plot_var)
        self.assertNotEqual(foo.name, 'failface.png')

