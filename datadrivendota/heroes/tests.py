"""
"""
from django.test import TestCase
# from django.test.client import Client
# from matches.tests import MatchValidityMixin


# TESTS
# @todo: Consider using factoryboy for generating test objects. It's a cool
# library!
# --kit 2014-02-16
class SimpleHeroUrlTest(TestCase):
    fixtures = ['test_fixture.json']

    def test_urls(self):
        urls = [
            '',
            'vitals/',
            'lineups/',
            'performance/',
            'performance-lineup/',
            'skillbuild-winrate/',
            'skill-progression/',
            'Juggernaut/',
            'ability/juggernaut_healing_ward/',
        ]
        for url in urls:
            strng = '/heroes/'+url
            resp = self.client.get(strng)
            self.assertEqual(resp.status_code, 200)

    # def test_vitals_api(self):
    #     strng = '/heroes/'+url
    #     resp = self.client.get(strng)

