from datetime import datetime, timedelta
from time import mktime
from django.conf import settings
from django.test import TestCase, Client
from datetime import timedelta
from django.utils import timezone
from teams.models import Team
from leagues.models import League, ScheduledMatch
from .json_samples import (
    good_league_schedule,
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
    UpdateLeagueSchedule,
    UpdateLiveGames,
    MirrorLeagues,
)
from model_mommy import mommy


class TestLeagueScheduleUpdate(TestCase):

    good_json = good_league_schedule

    def setUp(self):
        self.task = UpdateLeagueSchedule()
        self.old_match = mommy.make_recipe('leagues.scheduled_match')

    def test_cleaner(self):
        self.assertEqual(
            self.task.clean_urldata(self.good_json),
            self.good_json['result']

        )

    def test_deletion(self):
        self.task.delete_unscheduled_games(
            self.task.clean_urldata(self.good_json)
        )
        self.assertEqual(
            ScheduledMatch.objects.all().count(),
            0
        )

    def test_creation(self):
        self.task.delete_unscheduled_games(
            self.task.clean_urldata(self.good_json)
        )
        self.task.create_scheduled_games(
            self.task.clean_urldata(self.good_json)
        )
        self.assertEqual(
            ScheduledMatch.objects.all().count(),
            2
        )


class TestLiveGames(TestCase):
    good_json = good_live_games
    fixtures = ['heroes.json']

    @classmethod
    def setUpClass(self):
        super(self, TestLiveGames).setUpClass()
        self.task = UpdateLiveGames()

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


def remove_logo(team):
    team.valve_cdn_image = None
    team.save()


class TestModelMethods(TestCase):

    def setUp(self):
        self.league = mommy.make_recipe('leagues.league')

    def test_update_save(self):
        self.league.save()
        self.assertLess(
            timezone.now()-self.league.update_time,
            timedelta(seconds=.1)
        )

    def test_outdated(self):
        self.league.update_time = timezone.now() - timedelta(weeks=10)
        self.league.valve_cdn_image = None
        self.assertEqual(self.league.is_outdated, True)

        self.league.update_time = timezone.now() - timedelta(weeks=10)
        self.league.valve_cdn_image = 'http://www.whatever.com/test.png'
        self.assertEqual(self.league.is_outdated, True)

        self.league.update_time = timezone.now()
        self.league.valve_cdn_image = None
        self.assertEqual(self.league.is_outdated, True)

        self.league.update_time = timezone.now()
        self.league.valve_cdn_image = 'http://www.whatever.com/test.png'
        self.assertEqual(self.league.is_outdated, False)


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(self):
        super(TestUrlconf, self).setUpClass()
        self.league = mommy.make_recipe('leagues.league')

    def test_urls_ok(self):
        c = Client()

        resp = c.get('/leagues/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/leagues/{0}/'.format(self.league.steam_id))
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/leagues/scheduled-matches/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/leagues/live-game-detail/1/')
        self.assertEqual(resp.status_code, 200)
        # The magic is in the template, so any number is OK
