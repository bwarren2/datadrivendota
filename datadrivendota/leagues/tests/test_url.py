from django.test import TestCase, Client
from model_mommy import mommy


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUrlconf, cls).setUpClass()
        cls.league = mommy.make_recipe('leagues.league')

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
