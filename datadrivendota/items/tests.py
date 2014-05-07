from django.test import TestCase
from datadrivendota.test_mixins import UrlTestMixin


class SimpleItemUrlTest(UrlTestMixin, TestCase):
    fixtures = ['test_fixture.json']
    prefix = '/items/'
    simple_urls = ['', 'winrate/']
    api_urls = ['api/item-endgame/?hero=Juggernaut&skill_level=3&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&no_legend=true&width=275&height=275']
