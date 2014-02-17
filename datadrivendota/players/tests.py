
from django.test import TestCase
from .r import KDADensity, CountWinrate
from matches.test_mixins import MatchValidityMixin
from players.test_mixins import PlayerValidityMixin
import datetime


###TESTS
class KDADensityTestCase(PlayerValidityMixin, MatchValidityMixin, TestCase):
    fixtures = [
        'datadrivendota/heroes/test_data.json',
        'datadrivendota/matches/test_data.json'
    ]

    def setUp(self):
        super(KDADensityTestCase, self).setUp()

    def test_valid_call(self):
        foo = KDADensity(self.valid_player)
        self.assertNotEqual(foo.name, 'failface.png')

    def test_invalid_call(self):
        foo = KDADensity(self.invalid_player)
        self.assertEqual(foo.name, 'failface.png')


class CountWinrateTestCase(MatchValidityMixin, PlayerValidityMixin, TestCase):
    fixtures = [
        'datadrivendota/heroes/test_data.json',
        'datadrivendota/matches/test_data.json'
    ]

    def setUp(self):
        super(CountWinrateTestCase, self).setUp()

    def test_valid_call_defaults(self):
        foo = CountWinrate(player_id=self.valid_player)
        self.assertNotEqual(foo.name, 'failface.png')

    def test_valid_call(self):
        foo = CountWinrate(
            player_id=self.valid_player,
            game_mode_list=self.valid_game_modes,
            min_date=datetime.date(2009, 1, 1),
            max_date=datetime.datetime.now()
        )
        self.assertNotEqual(foo.name, 'failface.png')

    def test_invalid_players(self):
        foo = CountWinrate(
            player_id=self.invalid_player,
            game_mode_list=self.valid_game_modes,
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_modes(self):
        foo = CountWinrate(
            player_id=self.valid_player,
            game_mode_list=self.invalid_game_modes
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_date_order(self):
        foo = CountWinrate(
            player_id=self.valid_player,
            game_mode_list=self.valid_game_modes,
            min_date=datetime.date(2012, 1, 1),
            max_date=datetime.date(2009, 1, 1)
        )
        self.assertEqual(foo.name, 'failface.png')


class PlayerTimeline(MatchValidityMixin, PlayerValidityMixin, TestCase):
    fixtures = [
        'datadrivendota/heroes/test_data.json',
        'datadrivendota/matches/test_data.json'
    ]

    def setUp(self):
        super(PlayerTimeline, self).setUp()
