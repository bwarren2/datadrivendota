from django.test import TestCase, Client
from model_mommy import mommy


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUrlconf, cls).setUpClass()
        cls.league = mommy.make_recipe(
            'leagues.league',
            steam_id=100,
            tier=0
        )
        mommy.make_recipe(
            'matches.match',
            league=cls.league
        )

    def test_urls_ok(self):
        c = Client()

        resp = c.get('/leagues/')
        self.assertEqual(resp.status_code, 200)

        url = '/leagues/{0}/'.format(self.league.steam_id)
        resp = c.get(url)
        self.assertEqual(resp.status_code, 200)

        # The -1 represents a team that does not exist,
        # because steam ids are positive.
        resp = c.get('/leagues/{0}/'.format(-1))
        self.assertEqual(resp.status_code, 404)

        resp = c.get('/leagues/scheduled-matches/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/leagues/live-game-detail/1/')
        self.assertEqual(resp.status_code, 200)
        # The magic is in the template, so any number is OK
