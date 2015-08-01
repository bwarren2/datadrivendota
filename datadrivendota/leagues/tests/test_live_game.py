from django.test import TestCase
from .json_samples import (
    good_live_games,
    live_clean_url_json,
    live_get_players,
    live_game_data,
    live_side_data,
    live_pickbans,
    live_merge_logos,
    live_states,
)
from leagues.management.tasks import (
    UpdateLiveGames,
)


class TestLiveGames(TestCase):
    good_json = good_live_games
    fixtures = ['heroes.json']

    @classmethod
    def setUpClass(cls):
        super(cls, TestLiveGames).setUpClass()
        cls.task = UpdateLiveGames()

    def test_clean_url(self):

        self.assertEqual(
            self.task._clean_urldata(self.good_json),
            live_clean_url_json
        )

    def test_get_players(self):
        urldata = self.task._setup(self.good_json)
        lst = []
        for game in urldata:
            lst.append(self.task._get_players(game))

        self.assertEqual(
            lst,
            live_get_players
        )

    def test_get_pickbans(self):
        urldata = self.task._setup(self.good_json)
        lst = []
        for game in urldata:
            lst.append(self.task._get_pickbans(game))

        self.assertEqual(
            lst,
            live_pickbans
        )

    def test_get_game_data(self):
        urldata = self.task._setup(self.good_json)
        lst = []
        for game in urldata:
            lst.append(self.task._get_game_data(game))

        self.assertEqual(
            lst,
            live_game_data
        )

    def test_get_side_data(self):
        urldata = self.task._setup(self.good_json)
        lst = []
        for game in urldata:
            for side in ['radiant', 'dire']:
                lst.append(self.task._get_side_data(game, side))

        self.assertEqual(
            lst,
            live_side_data
        )

    def test_merge_logos(self):
        urldata = self.task._setup(self.good_json)

        # Or else get an error from get_or_create w/ sqlite
        data = self.task._merge_logos(urldata)

        self.assertEqual(data, live_merge_logos)

    def test_get_states(self):
        urldata = self.task._setup(self.good_json)

        lst = []
        for game in urldata:
            lst.append(self.task._get_states(game))

        self.assertEqual(
            lst,
            live_states
        )

    def test_store_data(self):
        pass

        # import json
        # with open('/home/ben/Projects/datadrivendota/datadrivendota/datadrivendota/leagues/tests/json_samples/live_states.json', 'w+') as f:
        #     f.write(json.dumps(lst))
