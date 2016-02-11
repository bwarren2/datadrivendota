from unittest import TestCase

import json
import responses
import requests

from django.utils.decorators import method_decorator
from django.conf import settings

from datadrivendota.management.tasks import ApiContext, ValveApiCall

from datadrivendota.tests import json_samples


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
        self.assertEqual(c.__repr__(), 'account_id: 5, ')

    def test_url_get(self):
        url = ApiContext().url_for('GetMatchHistory')
        answer = (
            'https://api.steampowered.com'
            '/IDOTA2Match_570/GetMatchHistory/v001/'
            '?skill=0&key={key}&matches_requested=100'
        ).format(key=settings.STEAM_API_KEY)
        self.assertEqual(url, answer)

        with self.assertRaises(KeyError):
            url = ApiContext().url_for('ABadMode')

    @method_decorator(responses.activate)
    def test_successful_run(self):
        url = (
            'https://api.steampowered.com'
            '/IDOTA2Match_570/GetMatchDetails/v001/'
            '?match_id=1950674785&key={key}'
        ).format(key=settings.STEAM_API_KEY)

        responses.add(
            responses.GET,
            url,
            body=json.dumps(json_samples.valid_match),
            status=200,
            content_type='application/json',
            match_querystring=True
        )
        api_context = ApiContext()
        api_context.match_id = 1950674785

        data = ValveApiCall().run('GetMatchDetails', api_context)

        self.assertEqual(
            {
                'api_context': api_context,
                'response_code': 200,
                'json_data': json_samples.valid_match,
                'url': url,
            },
            data
        )

    @method_decorator(responses.activate)
    def test_400_passthrough(self):
        url = (
            'http://api.steampowered.com'
            '/ISteamRemoteStorage/GetUGCFileDetails/v1/'
            '?ugcid=374974821137765&key={key}&appid=570'
        ).format(key=settings.STEAM_API_KEY)

        responses.add(
            responses.GET,
            url,
            body=json.dumps(json_samples.broken_ugc),
            status=404,
            content_type='application/json',
            match_querystring=True
        )
        api_context = ApiContext()
        api_context.ugcid = 374974821137765

        data = ValveApiCall().run('GetUGCFileDetails', api_context)
        self.assertEqual(
            {
                'api_context': api_context,
                'response_code': 404,
                'json_data': json_samples.broken_ugc,
                'url': url,
            },
            data
        )

    @method_decorator(responses.activate)
    def test_500_passthrough(self):
        url = (
            'http://api.steampowered.com'
            '/ISteamRemoteStorage/GetUGCFileDetails/v1/'
            '?ugcid=374974821137765&key={key}&appid=570'
        ).format(key=settings.STEAM_API_KEY)

        responses.add(
            responses.GET,
            url,
            body=json.dumps(json_samples.broken_ugc),
            status=504,
            content_type='application/json',
            match_querystring=True
        )
        api_context = ApiContext()
        api_context.ugcid = 374974821137765

        data = ValveApiCall().run('GetUGCFileDetails', api_context)
        self.assertEqual(
            {
                'api_context': api_context,
                'response_code': 504,
                'json_data': json_samples.broken_ugc,
                'url': url,
            },
            data
        )

    @method_decorator(responses.activate)
    def test_json_fixing(self):
        url = 'http://www.google.com'

        responses.add(
            responses.GET,
            url,
            body='',
            status=200,
        )
        r = requests.get(url)
        data = ValveApiCall().get_json(r, url)
        self.assertEqual({}, data)
