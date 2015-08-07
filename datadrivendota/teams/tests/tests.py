from django.test import TestCase, Client
from model_mommy import mommy
from django.utils import timezone
from datetime import timedelta


class TestModelMethods(TestCase):

    def setUp(self):
        self.team = mommy.make_recipe('teams.team')

    def test_update_save(self):
        self.team.save()
        self.assertLess(
            timezone.now() - self.team.update_time,
            timedelta(seconds=.1)
        )

    def test_outdated(self):
        self.team.update_time = timezone.now() - timedelta(weeks=10)
        self.team.valve_cdn_image = None
        self.assertEqual(self.team.is_outdated, True)

        self.team.update_time = timezone.now() - timedelta(weeks=10)
        self.team.valve_cdn_image = 'http://www.whatever.com/test.png'
        self.assertEqual(self.team.is_outdated, False)

        self.team.update_time = timezone.now()
        self.team.valve_cdn_image = None
        self.assertEqual(self.team.is_outdated, False)

        self.team.update_time = timezone.now()
        self.team.valve_cdn_image = 'http://www.whatever.com/test.png'
        self.assertEqual(self.team.is_outdated, False)


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUrlconf, cls).setUpClass()
        cls.team = mommy.make_recipe('teams.team')

    def test_url_ok(self):
        c = Client()

        resp = c.get('/teams/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/teams/{0}/'.format(self.team.steam_id))
        self.assertEqual(resp.status_code, 200)

        # The -1 represents a team that does not exist,
        # because steam ids are positive.
        resp = c.get('/teams/{0}/'.format(-1))
        self.assertEqual(resp.status_code, 404)
