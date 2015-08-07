from django.test import TestCase, Client
from model_mommy import mommy


class TestMommy(TestCase):

    def test_mommy(self):
        mommy.make_recipe('players.player')


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUrlconf, cls).setUpClass()
        cls.player = mommy.make_recipe('players.player')

    def test_url_ok(self):
        c = Client()

        resp = c.get('/players/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/players/all-players/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/players/{0}/'.format(self.player.steam_id))
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/players/{0}/'.format(-1))
        self.assertEqual(resp.status_code, 404)

    def test_url_login(self):
        c = Client()
        resp = c.get('/players/followed/')
        self.assertEqual(resp.status_code, 302)
        # We need to refactor the permissions conventions as well.
        # Test success later.
