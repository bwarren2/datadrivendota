import gc
import requests
from time import time as now
from urllib import urlencode
from celery import Task
from celery.exceptions import (
    SoftTimeLimitExceeded,
    TimeLimitExceeded,
    WorkerLostError,
)
from datadrivendota.settings.base import STEAM_API_KEY
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

    def to_url_dict(self, mode):
        """
        These are hardcoded per the valve spec.  Annoying.
        """

        if mode == 'GetPlayerSummaries':
            valve_url_vars = ['steamids', 'key']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetTeamInfoByTeamID':
            valve_url_vars = ['key', 'start_at_team_id', 'teams_requested']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetUGCFileDetails':
            valve_url_vars = ['key', 'ugcid', 'appid']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetLeagueListing':
            valve_url_vars = ['key']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetSchema':
            valve_url_vars = ['key']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetSchemaURL':
            valve_url_vars = ['key']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetItemIconPath':
            valve_url_vars = ['key', 'format', 'iconname']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetPlayerOfficialInfo':
            valve_url_vars = ['key', 'AccountID']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetMatchDetails':
            valve_url_vars = ['match_id', 'key']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetTournamentPlayerStats':
            valve_url_vars = ['league_id', 'account_id', 'key']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetScheduledLeagueGames':
            valve_url_vars = ['date_min', 'date_max', 'key']
            return self.dict_vars(valve_url_vars)
        elif mode == 'GetLiveLeagueGames':
            valve_url_vars = ['key']
            return self.dict_vars(valve_url_vars)
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
            return self.dict_vars(valve_url_vars)
        else:
            logger.warning("I did not understand mode: " + mode)

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
                'https://api.steampowered.com/IEconDOTA2_570/'
                'GetHeroes/v0001/'
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
                'https://api.steampowered.com/IEconDOTA2_570/'
                'GetItemIconPath/v1/'
            ),
            'GetPlayerOfficialInfo': (
                'https://api.steampowered.com/IDOTA2Fantasy_570/'
                'GetPlayerOfficialInfo/v1/'
            ),
            'GetUGCFileDetails': (
                'http://api.steampowered.com/ISteamRemoteStorage/'
                'GetUGCFileDetails/v1/'
            ),
            'GetTournamentPlayerStats': (
                'http://api.steampowered.com/IDOTA2Match_570/'
                'GetTournamentPlayerStats/v1/'
            ),
            'GetScheduledLeagueGames': (
                'http://api.steampowered.com/IDOTA2Match_570/'
                'GetScheduledLeagueGames/V001/'
            ),

        }
        try:
            return mode_dict[mode]
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
                    strng += "{0}: {1} \n".format(field, getattr(self, field))

        return strng

    def __repr__(self):
        return self.__str__()


# Parents
class BaseTask(Task):

    """A subcase of celery tasks with a api context and garbage collection. """

    abstract = True

    def __call__(self, *args, **kwargs):
        """ Expect an ApiContext instance in calling. """
        self.api_context = kwargs['api_context']
        del kwargs['api_context']
        return super(BaseTask, self).__call__(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # Optimization hack in heroku instances.
        gc.collect()

    # There are also hooks for retry, fail, and success actions.


class ApiFollower(Task):

    """ Expect an api context and a result. """

    abstract = True

    def __call__(self, *args, **kwargs):
        self.result = args[0].get('result', {})
        self.api_context = args[0].get('api_context', {})
        return super(ApiFollower, self).__call__(*args, **kwargs)


# Descendants
class ValveApiCall(BaseTask):
    def run(self, mode, **kwargs):
        """
        Ping the valve API for downloading results.

        We do have exactly one task that interacts with valve's api to enable
        rate limiting.  Check celery config/env for that metering.

        For lots more docs, see http://dev.dota2.com/showthread.php?t=58317
        """
        try:

            url = self.api_context.url_for(mode)

            # We could use payload, but this is easier to log.
            URL = url + '?' + urlencode(self.api_context.to_url_dict(mode))
            logger.info("Hitting valve API for URL: " + URL)

            # Exception handling for the URL opening.
            try:
                response = requests.get(URL, timeout=5)
                if response.status_code != 200:
                    if response.status_code in [104, 111]:
                        logger.warning(
                            "Got error code {0} for {1}.  Retrying. ".format(
                                response.status_code, URL
                            )
                        )
                        self.retry(mode=mode)

                    elif 400 <= response.status_code < 500:
                        logger.error(
                            "Got a 4XX code for {0}.  Not Retrying.".format(
                                URL
                            )
                        )
                    elif 500 <= response.status_code < 600:
                        logger.error(
                            "Got a 5XX code for {0}.  Not Retrying.".format(
                                URL
                            )
                        )
                    else:
                        response.raise_for_status()

            except requests.exceptions.Timeout:
                logger.warning("Timed out for {0}.  Retrying.".format(URL))
                self.retry(mode=mode)

            # If everything is kosher, import the result and return it.
            data = response.json()
            data['api_context'] = self.api_context
            return data

        except SoftTimeLimitExceeded as exc:
            logger.warning("Soft timeout for {0}.  Retrying.".format(URL))
            self.retry(mode=mode, exc=exc)
        except WorkerLostError as exc:
            logger.warning("Worker lost for {0}.  Retrying.".format(URL))
            self.retry(mode=mode, exc=exc)
        except TimeLimitExceeded as exc:
            logger.warning("Time exceeded for {0}.  Retrying.".format(URL))
            self.retry(mode=mode, exc=exc)
