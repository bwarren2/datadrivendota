from django.test import TestCase, Client
from django.conf import settings
from model_mommy import mommy
from accounts.mommy_recipes import make_full_customer, make_user
from players.management.tasks import MirrorClientMatches, MirrorUserMatches


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

        resp = c.get('/players/{0}/'.format(self.player.steam_id))
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/players/{0}/'.format(-1))
        self.assertEqual(resp.status_code, 404)


class TestUserMatches(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUserMatches, cls).setUpClass()
        # cls.userprofile = mommy.make_recipe('accounts.userprofile')
        cls.paid_user = make_full_customer(
            'steve', 'imsteve@gmail.com', 101010
        )
        cls.unpaid_user = make_user('bob', 'bob@gmail.com', 222222)
        cls.inactive_user = make_user(
            'ted', 'ted@gmail.com', 333333, active=False
        )

    def test_client_get(self):
        clients = MirrorClientMatches().get_users()
        self.assertEqual(list(clients),
            [self.paid_user.userprofile.steam_id] + settings.TESTERS
            )

    def test_active_get(self):
        active_users = MirrorUserMatches().get_users()
        self.assertEqual(
            list(active_users),
            [
                self.paid_user.userprofile.steam_id,
                self.unpaid_user.userprofile.steam_id,
            ]
        )
