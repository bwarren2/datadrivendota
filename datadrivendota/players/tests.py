from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from datadrivendota.test_mixins import UrlTestMixin


###TESTS
class SimplePlayerUrlTest(UrlTestMixin, TestCase):
    fixtures = ['test_fixture.json']
    prefix = '/players/'
    simple_urls = [
        '',
        'all-players/',
        'winrate/',
        'hero-adversary/',
        'hero-ability-comparison/',
    ]
    api_urls = [
        'api/hero-abilities/?player_1=Na%60Vi.Dendi&hero_1=Juggernaut&player_2=%5BA%5D+s4+HyperX&hero_2=Juggernaut&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&division=Players',
        'api/winrate/?player=Na%60Vi.Dendi&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&min_date=2009-04-07&max_date=2014-05-07&group_var=hero',
        'api/hero-adversary/?player=Na%60Vi.Dendi&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&min_date=2009-04-01&max_date=2014-04-13&group_var=hero&plot_var=winrate',
        'api/versus-winrate/?player_1=Na%60Vi.Dendi&player_2=%5BA%5D+s4+HyperX&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&group_var=alignment&plot_var=usage&width=300&height=300',
        'api/role/?player_1=Na%60Vi.Dendi&player_2=%5BA%5D+s4+HyperX&plot_var=games&width=300&height=300',
        ]

# class LoginUrlTest(TestCase):

#     def test_login_urls_redirect(self):
#         urls = ['followed/', 'management/']
#         for url in urls:
#             strng = '/players/'+url
#             resp = self.client.get(strng)
#             self.assertEqual(resp.status_code, 302)


# class LoginUserUrlTest(TestCase):
#     def setUp(self):
#         User.objects.create_user(
#             'temporary',
#             'temporary@gmail.com',
#             'temporary'
#         )
#         super(LoginUserUrlTest, self).setUp()

#     def test_login_urls_OK(self):
#         c = Client()
#         c.login(username='temporary', password='temporary')
#         urls = ['followed/', 'management/']
#         for url in urls:
#             strng = '/players/'+url
#             resp = self.client.get(strng)
#             self.assertEqual(resp.status_code, 302)
