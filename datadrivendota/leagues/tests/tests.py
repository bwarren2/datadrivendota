from cStringIO import StringIO
from django_nose import FastFixtureTestCase
from datetime import timedelta
from django.utils import timezone
from django.core.files import File
from django.test import TestCase
from teams.models import Team
from leagues.json_data import league_winrate_json
from leagues.models import League, ScheduledMatch
from matches.mommy_recipes import make_matchset
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
from leagues.management.tasks import UpdateLeagueSchedule, UpdateLiveGames
from model_mommy import mommy


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

    def test_object_outdated(self):
        self.task.delete_unscheduled_games(
            self.task.clean_urldata(self.good_json)
        )
        self.task.create_scheduled_games(
            self.task.clean_urldata(self.good_json)
        )

        for team in Team.objects.all():
            team.valve_cdn_image = None
            team.save()

        test_team = Team.objects.all()[0]
        test_team.valve_cdn_image = 'http://www.whatever.com/test.png'
        test_team.save()
        # Has logo image, recent update time
        self.assertEqual(self.task._object_outdated(test_team), False)

        # Has logo image, old update time
        test_team.update_time = timezone.now() - timedelta(days=10)
        test_team.valve_cdn_image = 'http://www.whatever.com/test.png'
        test_team.save()
        self.assertEqual(self.task._object_outdated(test_team), True)

        # Has no logo image, old update time
        test_team.valve_cdn_image = ''
        test_team.save()
        self.assertEqual(self.task._object_outdated(test_team), True)

        # Has no logo image, new update time
        test_team.update_time = timezone.now()
        test_team.save()
        self.assertEqual(self.task._object_outdated(test_team), True)

    def test_find_update_teams(self):
        data = self.task.clean_urldata(self.good_json)
        self.task.delete_unscheduled_games(
            self.task.clean_urldata(self.good_json)
        )
        self.task.create_scheduled_games(
            self.task.clean_urldata(self.good_json)
        )
        teams = []
        for game in data['games']:

            t = Team.objects.get(steam_id=game['teams'][0]['team_id'])
            remove_logo(t)
            teams.append(t)

            t = Team.objects.get(steam_id=game['teams'][1]['team_id'])
            remove_logo(t)
            teams.append(t)

        teams[0].update_time = timezone.now() - timedelta(weeks=20)
        teams[0].save()
        teams[2].valve_cdn_image = None
        teams[2].save()

        # print "Expected: {0}".format([teams[0].steam_id, teams[2].steam_id])
        # print "Got: {0}".format(self.task.find_update_teams(data))
        self.assertEqual(
            [teams[0].steam_id, teams[2].steam_id],
            self.task.find_update_teams(data)
        )

    def test_find_update_leagues(self):

        data = self.task.clean_urldata(self.good_json)
        self.task.delete_unscheduled_games(
            self.task.clean_urldata(self.good_json)
        )
        self.task.create_scheduled_games(
            self.task.clean_urldata(self.good_json)
        )

        leagues = []
        for game in data['games']:

            l = League.objects.get(steam_id=game['league_id'])
            remove_logo(l)
            leagues.append(l)

        # Make a league look very out of date
        leagues[0].update_time = timezone.now() - timedelta(weeks=20)
        leagues[0].save()

        self.assertEqual(
            [leagues[0].steam_id],
            self.task.find_update_leagues(data)
        )


class TestLiveGames(FastFixtureTestCase):
    good_json = good_live_games
    fixtures = ['heroes.json']

    def setUp(self):
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
        import json
        for game in urldata:
            print json.dumps(game)
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
        from django.db import transaction
        transaction.set_autocommit(True)
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
