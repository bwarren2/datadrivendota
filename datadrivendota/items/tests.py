from django.test import TestCase
from datadrivendota.test_mixins import UrlTestMixin


class SimpleItemUrlTest(UrlTestMixin, TestCase):
    fixtures = ['test_fixture.json']
    prefix = '/items/'
    simple_urls = ['', 'winrate/']
    api_urls = []
