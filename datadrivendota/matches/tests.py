"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase


# TESTS
class SimpleMatchUrlTest(TestCase):
    fixtures = ['test_fixture.json']

    def test_urls(self):
        urls = [
            '',
            'follow-matches/',
            'endgame/', 'team-endgame/',
            'own-team-endgame/',
            'ability-build/',
            'progression-list/',
        ]
        for url in urls:
            strng = '/matches/'+url
            resp = self.client.get(strng)
            self.assertEqual(resp.status_code, 200)
