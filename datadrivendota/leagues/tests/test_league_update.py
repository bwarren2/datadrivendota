from django.test import TestCase
from leagues.management.tasks import (
    UpdateLeagues,
)
from .json_samples import league_schema
from leagues.models import League


class TestLeagueCreate(TestCase):
    good_json = league_schema

    @classmethod
    def setUpClass(cls):
        super(cls, TestLeagueCreate).setUpClass()
        cls.task = UpdateLeagues()

    def test_get_tier(self):
        self.assertEqual(
            self.task._get_tier(league_schema[2733], 2733),
            League.PREMIUM
        )

        self.assertEqual(
            self.task._get_tier(league_schema[1234], 1234),
            League.AMATEUR
        )

        self.assertEqual(
            self.task._get_tier(league_schema[007], 007),
            League.PRO
        )

        self.assertEqual(
            self.task._get_tier(league_schema[10], 10),
            None
        )

        with self.assertRaises(Exception):
            self.task._get_tier(league_schema[4444], 4444)

    def test_get_fantasy(self):

        self.assertEqual(
            self.task._get_fantasy(league_schema[2733], 2733),
            True
        )

        self.assertEqual(
            self.task._get_fantasy(league_schema[1234], 1234),
            False
        )

        self.assertEqual(
            self.task._get_fantasy(league_schema[007], 007),
            None
        )

        with self.assertRaises(Exception):
            self.task._get_fantasy(league_schema[10], 10)

    def test_create(self):
        self.task.schema = league_schema
        self.task.create(2733)
        l = League.objects.get(steam_id=2733)

        self.assertEqual(l.name, league_schema[2733]['name'])
        self.assertEqual(
            l.description, league_schema[2733]['item_description']
        )
        self.assertEqual(
            l.tournament_url, league_schema[2733]['tournament_url']
        )
        self.assertEqual(l.item_def, 16413)
        self.assertEqual(l.tier, League.PREMIUM)
        self.assertEqual(l.fantasy, True)
