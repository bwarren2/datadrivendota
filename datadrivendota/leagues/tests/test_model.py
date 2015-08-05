from datetime import timedelta
from django.test import TestCase
from django.utils import timezone

from model_mommy import mommy


class TestModelMethods(TestCase):

    def setUp(self):
        self.league = mommy.make_recipe('leagues.league')

    def test_update_save(self):
        self.league.save()
        self.assertLess(
            timezone.now() - self.league.update_time,
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
