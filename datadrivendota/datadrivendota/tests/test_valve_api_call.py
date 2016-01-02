from unittest import TestCase

import responses
import requests

from django.utils.decorators import method_decorator

from datadrivendota.management.tasks import ApiContext


class TestValveApiCall(TestCase):

    @method_decorator(responses.activate)
    def test_foo(self):
        responses.add(
            responses.GET,
            'http://twitter.com/api/1/foobar',
            body='{"error": "not found"}',
            status=404,
            content_type='application/json'
        )

        resp = requests.get('http://twitter.com/api/1/foobar')
        self.assertEqual(resp.json(), {"error": "not found"})


class TestApiContext(TestCase):

    def test_repr(self):
        c = ApiContext()
        c.account_id = 5
        self.assertEqual(c.__repr__(), 'account_id: 5 \n')

    def test_url_get(self):
        url = ApiContext().url_for('GetMatchHistory')
        answer = (
            'https://api.steampowered.com'
            '/IDOTA2Match_570/GetMatchHistory/v001/'
        )
        self.assertEqual(url, answer)

        with self.assertRaises(KeyError):
            url = ApiContext().url_for('ABadMode')
