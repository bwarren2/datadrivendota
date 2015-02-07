from cStringIO import StringIO
from datetime import timedelta
from django.utils import timezone
from django.core.files import File
from django.test import TestCase
from teams.models import Team
from leagues.json_data import league_winrate_json
from leagues.models import League, ScheduledMatch
from matches.mommy_recipes import make_matchset
from .json_samples import good_league_schedule, good_live_games
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
            fake_logo(team)

        test_team = Team.objects.all()[0]
        # Has logo image, recent update time
        self.assertEqual(self.task._object_outdated(test_team), False)

        # Has logo image, old update time
        test_team.update_time = timezone.now() - timedelta(days=10)
        test_team.save()
        self.assertEqual(self.task._object_outdated(test_team), True)

        # Has no logo image, old update time
        test_team.logo_image.delete()
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
            fake_logo(t)
            teams.append(t)

            t = Team.objects.get(steam_id=game['teams'][1]['team_id'])
            fake_logo(t)
            teams.append(t)

        teams[0].update_time = timezone.now() - timedelta(weeks=20)
        teams[0].save()
        teams[2].logo_image.delete()

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
            fake_logo(l)
            leagues.append(l)

        # Make a league look very out of date
        leagues[0].update_time = timezone.now() - timedelta(weeks=20)
        leagues[0].save()

        self.assertEqual(
            [leagues[0].steam_id],
            self.task.find_update_leagues(data)
        )


class TestLiveGames(TestCase):
    good_json = good_live_games

    def setUp(self):
        self.task = UpdateLiveGames()
        self.old_match = mommy.make_recipe('leagues.scheduled_match')

    def test_logo_monkeying(self):
        print '#####'
        print self.good_json
        print self.task.merge_logos(self.good_json)
        print '#####'
        raise Exception


def fake_logo(obj):
    fakery = StringIO()
    fakery.write('foo')
    obj.logo_image.save('binky.jpg', File(fakery))
