from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from model_mommy import mommy


class TestUrlconf(TestCase):
    username = 'superman'
    password = 'wordpass'
    email = 'supes@hotmail.com'

    def setUp(self):
        User.objects.create_superuser(
            username=self.username, email=self.email, password=self.password
        )
        self.client = Client()

        # Cards wants data to render
        self.hero = mommy.make_recipe('heroes.hero', visible=True)
        self.match = mommy.make_recipe('matches.match')
        self.pms = mommy.make_recipe('matches.playermatchsummary')
        self.player = mommy.make_recipe('players.player')

    def test_login_required(self):
        self.client.login(username=self.username, password=self.password)

        urls = ['/health/', '/health/styles/', '/health/cards/']
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)

    def tearDown(self):
        self.client.logout()
