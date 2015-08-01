from django.test import TestCase
from leagues.models import ScheduledMatch
from .json_samples import (
    good_league_schedule,
)
from leagues.management.tasks import (
    UpdateLeagueSchedule,
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
