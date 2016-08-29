import gc
import requests
from time import time as now
from purl import URL

from celery import Task
from celery.exceptions import (
    SoftTimeLimitExceeded,
    TimeLimitExceeded,
    WorkerLostError,
)

from datadrivendota.settings.base import STEAM_API_KEY
from datadrivendota.exceptions import EmptyResponseException

import logging
logger = logging.getLogger(__name__)


class ApiContext(object):

    """
    A box of configuration for interacting with Valve's API.

    Keeps track of things like the steam API key,
    what the parameter names valve recognizes are,
    and sane default options.
    """

    account_id = None
    iconname = None
    matches_requested = 100
    skill = 0
    date_max = None
    start_at_match_id = None
    key = None
    match_id = None
    hero_id = None
    tournament_games_only = None
    format = 'json'
    # There are magic lists of the above in the URL constructor.

    # Things we care about internally
    start_scrape_time = None
    matches_desired = None
    skill_levels = [0]  # This only works for heroes.
    deepcopy = False
    last_scrape_time = 0
    steamids = None
    processed = 0
    refresh_records = False
    date_pull = False
    appid = 570  # Only matters for ugc acquisition

    def __init__(self, *args, **kwargs):
        self.start_scrape_time = now()
        self.key = STEAM_API_KEY
        super(ApiContext, self).__init__(*args, **kwargs)

    def to_url_dict(self, mode):  # NOQA: this has high mccabe complexity
        """
        These are hardcoded per the valve spec.  Annoying.
        """

        if mode == 'GetPlayerSummaries':
            valve_url_vars = [
                'steamids',
                'key',
            ]
        elif mode == 'GetTeamInfoByTeamID':
            valve_url_vars = [
                'key',
                'start_at_team_id',
                'teams_requested',
            ]
        elif mode == 'GetUGCFileDetails':
            valve_url_vars = [
                'key',
                'ugcid',
                'appid',
            ]
        elif mode == 'GetLeagueListing':
            valve_url_vars = [
                'key',
            ]
        elif mode == 'GetSchema':
            valve_url_vars = [
                'key',
            ]
        elif mode == 'GetSchemaURL':
            valve_url_vars = [
                'key',
            ]
        elif mode == 'GetItemIconPath':
            valve_url_vars = [
                'key',
                'format',
                'iconname',
            ]
        elif mode == 'GetPlayerOfficialInfo':
            valve_url_vars = [
                'key',
                'AccountID',
            ]
        elif mode == 'GetMatchDetails':
            valve_url_vars = [
                'match_id',
                'key',
            ]
        elif mode == 'GetTournamentPlayerStats':
            valve_url_vars = [
                'league_id',
                'account_id',
                'key',
            ]
        elif mode == 'GetScheduledLeagueGames':
            valve_url_vars = [
                'date_min',
                'date_max',
                'key',
            ]
        elif mode == 'GetLiveLeagueGames':
            valve_url_vars = [
                'key',
            ]
        elif mode == 'GetMatchHistory':
            valve_url_vars = [
                'account_id',
                'hero_id',
                'matches_requested',
                'skill',
                'league_id',
                'date_min',
                'date_max',
                'start_at_match_id',
                'key',
            ]
        elif mode == 'GetMatchHistoryBySequenceNum':
            valve_url_vars = [
                'key',
                'start_at_match_seq_num',
                'matches_requested',
            ]
        else:
            logger.warning("I did not understand mode: " + mode)
        return self.dict_vars(valve_url_vars)

    def dict_vars(self, url_vars):
        return_dict = {}
        for var in url_vars:
            if getattr(self, var, None) is not None:
                return_dict[var] = getattr(self, var)
        return return_dict

    def url_for(self, mode):
        mode_dict = {
            'GetMatchHistory': (
                'https://api.steampowered.com'
                '/IDOTA2Match_570/GetMatchHistory/v001/'
            ),
            'GetMatchDetails': (
                'https://api.steampowered.com'
                '/IDOTA2Match_570/GetMatchDetails/v001/'
            ),
            'GetHeroes': (
                'https://api.steampowered.com'
                '/IEconDOTA2_570/GetHeroes/v0001/'
            ),
            'GetPlayerSummaries': (
                'https://api.steampowered.com'
                '/ISteamUser/GetPlayerSummaries/v0002/'
            ),
            'EconomySchema': (
                'https://api.steampowered.com/IEconItems_570/'
                'GetSchema/v0001/'
            ),
            'GetLeagueListing': (
                'https://api.steampowered.com'
                '/IDOTA2Match_570/GetLeagueListing/v0001/'
            ),
            'GetLiveLeagueGames': (
                'https://api.steampowered.com'
                '/IDOTA2Match_570/GetLiveLeagueGames/v0001/'
            ),
            'GetMatchHistoryBySequenceNum': (
                'https://api.steampowered.com'
                '/IDOTA2Match_570/GetMatchHistoryBySequenceNum/v0001/'
            ),
            'GetTeamInfoByTeamID': (
                'https://api.steampowered.com'
                '/IDOTA2Match_570/GetTeamInfoByTeamID/v001/'
            ),
            'GetSchema': (
                'https://api.steampowered.com'
                '/IEconItems_570/GetSchema/v0001/'
            ),
            'GetSchemaURL': (
                'https://api.steampowered.com'
                '/IEconItems_570/GetSchemaURL/v1/'
            ),
            'GetItemIconPath': (
                'https://api.steampowered.com'
                '/IEconDOTA2_570/GetItemIconPath/v1/'
            ),
            'GetPlayerOfficialInfo': (
                'https://api.steampowered.com'
                '/IDOTA2Fantasy_570/GetPlayerOfficialInfo/v1/'
            ),
            'GetUGCFileDetails': (
                'http://api.steampowered.com'
                '/ISteamRemoteStorage/GetUGCFileDetails/v1/'
            ),
            'GetTournamentPlayerStats': (
                'http://api.steampowered.com'
                '/IDOTA2Match_570/GetTournamentPlayerStats/v1/'
            ),
            'GetScheduledLeagueGames': (
                'http://api.steampowered.com'
                '/IDOTA2Match_570/GetScheduledLeagueGames/V001/'
            ),

        }
        try:

            url = URL.from_string(mode_dict[mode])
            for k, v in self.to_url_dict(mode).iteritems():
                url = url.query_param(k, v)

            return url.as_string()

        except KeyError:
            logger.error("What is this mode? {0}".format(mode))
            raise

    def __str__(self):
        """
        APIContexts get printed in error strings, so make them pretty.
        """
        strng = ''
        for field in [
            'account_id',
            'iconname',
            'matches_requested',
            'skill',
            'date_max',
            'date_min',
            'start_at_match_id',
            'match_id',
            'league_id',
            'hero_id',
            'matches_desired'
            'skill_levels',
            'deepcopy',
            'steamids',
            'processed',
            'refresh_records',
            'date_pull',
            'tournament_games_only',
        ]:
            if hasattr(self, field):
                value = getattr(self, field, None)
                default_value = getattr(self.__class__, field, None)
                if value is not None and value != default_value:
                    strng += "{0}: {1}, ".format(field, getattr(self, field))

        return strng

    def __repr__(self):
        return self.__str__()

    @property
    def desired(self):
        """ Type info gets lost in deserialization. """
        return int(self.matches_desired)


# Parents
class BaseTask(Task):

    """A subcase of celery tasks with garbage collection. """

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # Optimization hack in heroku instances.
        gc.collect()

    # There are also hooks for retry, fail, and success actions.


class ApiFollower(BaseTask):

    """

    Expect run() called with:
        an api context, a result, a status code, and a url.
    """
    abstract = True

    def __call__(self, *args, **kwargs):
        # We can only return 1 thing in a chain,
        # but want to pass 4 to api-following run() calls.
        if len(args) == 1 and isinstance(args[0], dict):
            kwargs.update(args[0])
            args = ()
        return super(ApiFollower, self).__call__(*args, **kwargs)


# Descendants
class ValveApiCall(BaseTask):
    def run(self, mode, api_context, **kwargs):
        """
        Ping the valve API for downloading results.

        We have exactly one task that interacts with valve's api to enable rate
        limiting.  Check celery config/env for that metering.  This task
        primarily does dumb passthrough; downstream tasks are responsible for
        interpreting the (various) ways things can fail.

        For lots more docs, see http://dev.dota2.com/showthread.php?t=58317
        """
        try:

            api_url = api_context.url_for(mode)
            logger.info("Hitting valve API for URL: " + api_url)

            response = self.get_response(api_url, mode)

            json_data = self.get_json(response, api_url)

            empty_failure_modes = ['GetMatchDetails', 'GetMatchHistory']
            if json_data == {} and mode in empty_failure_modes:
                self.retry(mode=mode, exc=EmptyResponseException)

            return {
                'api_context': api_context,
                'response_code': response.status_code,
                'json_data': json_data,
                'url': api_url,
            }

        except SoftTimeLimitExceeded as exc:
            logger.warning("Soft timeout for {0}.  Retrying.".format(api_url))
            self.retry(mode=mode, exc=exc)
        except WorkerLostError as exc:
            logger.warning("Worker lost for {0}.  Retrying.".format(api_url))
            self.retry(mode=mode, exc=exc)
        except TimeLimitExceeded as exc:
            logger.warning("Time exceeded for {0}.  Retrying.".format(api_url))
            self.retry(mode=mode, exc=exc)

    def get_response(self, api_url, mode):
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code != 200:
                if response.status_code in [104, 111]:
                    logger.warning(
                        "Got error code {0} for {1}.  Retrying. ".format(
                            response.status_code, api_url
                        )
                    )
                    self.retry(mode=mode)

                elif 400 <= response.status_code < 500:
                    logger.warning(
                        "Got a 4XX code for {0}.  Not Retrying.".format(
                            api_url
                        )
                    )
                elif 500 <= response.status_code < 600:
                    logger.warning(
                        "Got a 5XX code for {0}.  Not Retrying.".format(
                            api_url
                        )
                    )
                else:
                    response.raise_for_status()

        except requests.exceptions.Timeout:
            logger.warning("Timed out for {0}.  Retrying.".format(api_url))
            self.retry(mode=mode)

        return response

    def get_json(self, response, api_url):
        try:
            json_data = response.json()
        except ValueError:
            # Technically this is not the thrown error, but read
            # http://stackoverflow.com/questions/8381193/python-handle-json-decode-error-when-nothing-returned
            logger.exception('JSON decode error for url {0}'.format(api_url))
            json_data = {}

        return json_data
