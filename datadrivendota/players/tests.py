from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client


###TESTS
class SimplePlayerUrlTest(TestCase):
    fixtures = ['datadrivendota/heroes/test_fixture.json']

    def test_urls_OK(self):
        urls = [
            '', 'all-players/',
            'winrate/', 'hero-adversary/',
            'hero-ability-comparison/',
        ]
        for url in urls:
            strng = '/players/'+url
            resp = self.client.get(strng)
            self.assertEqual(resp.status_code, 200)

    def test_login_urls_redirect(self):
        urls = ['followed/', 'management/']
        for url in urls:
            strng = '/players/'+url
            resp = self.client.get(strng)
            self.assertEqual(resp.status_code, 302)


class LoginUserUrlTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            'temporary',
            'temporary@gmail.com',
            'temporary'
        )
        super(LoginUserUrlTest, self).setUp()

    def test_login_urls_OK(self):
        c = Client()
        c.login(username='temporary', password='temporary')
        urls = ['followed/', 'management/']
        for url in urls:
            strng = '/players/'+url
            resp = self.client.get(strng)
            self.assertEqual(resp.status_code, 302)
