from httplib import BadStatusLine
from copy import deepcopy
import gc
import urllib2
import json
import socket
import ssl
from time import time as now
from urllib import urlencode
from celery import Task, chain
from celery.exceptions import (
    SoftTimeLimitExceeded,
    MaxRetriesExceededError,
    TimeLimitExceeded,
    WorkerLostError,
    )
from datadrivendota.settings.base import STEAM_API_KEY
import logging
from utils import send_error_email
from players.models import Player
from matches.management.tasks import UpdateMatch
# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
import os
os.environ['http_proxy'] = ''
# End Patch


logger = logging.getLogger(__name__)


class ApiContext(object):
    """
    A box of configuration for interacting with Valve's API.

    Keeps track of things like the steam API key, what the parameter names valve recognizes are, and sane default options.
    """

    account_id = None
    matches_requested = 100
    skill = 0
    date_max = None
    start_at_match_id = None
    key = None
    match_id = None
    hero_id = None
    tournament_games_only = None
    # There are magic lists of teh above in the URL constructor.

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

    def toUrlDict(self, mode):
        if mode == 'GetPlayerSummaries':
            valve_URL_vars = ['steamids', 'key']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetTeamInfoByTeamID':
            valve_URL_vars = ['key', 'start_at_team_id', 'teams_requested']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetUGCFileDetails':
            valve_URL_vars = ['key', 'ugcid', 'appid']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetLeagueListing':
            valve_URL_vars = ['key']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetSchema':
            valve_URL_vars = ['key']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetPlayerOfficialInfo':
            valve_URL_vars = ['key', 'AccountID']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetMatchDetails':
            valve_URL_vars = ['match_id', 'key']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetTournamentPlayerStats':
            valve_URL_vars = ['league_id', 'account_id', 'key']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetScheduledLeagueGames':
            valve_URL_vars = ['date_min', 'date_max', 'key']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetMatchHistory':
            valve_URL_vars = [
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
            return self.dictVars(valve_URL_vars)
        else:
            logger.error("I did not understand mode: "+mode)

    def dictVars(self, url_vars):
        return_dict = {}
        for var in url_vars:
            if getattr(self, var, None) is not None:
                return_dict[var] = getattr(self, var)
        return return_dict

    def __str__(self):

        strng = ''
        for field in [
            'account_id',
            'matches_requested',
            'skill',
            'date_max',
            'date_min',
            'start_at_match_id',
            'key',
            'match_id',
            'league_id',
            'hero_id',
            'start_scrape_time',
            'matches_desired'
            'skill_levels',
            'deepcopy',
            'last_scrape_time',
            'steamids',
            'processed',
            'refresh_records',
            'date_pull',
            'tournament_games_only',
        ]:
            if hasattr(self, field):
                if getattr(self, field) is not None:
                    strng += "{0}: {1} \n".format(field, getattr(self, field))

        return strng

    def __repr__(self):
        return self.__str__()


# Parents
class BaseTask(Task):
    """
    A subcase of celery tasks with a magic api context and garbage collection
    """
    abstract = True

    def __call__(self, *args, **kwargs):
        """
        Expects an ApiContext instance in calling.
        """
        self.api_context = kwargs['api_context']
        del kwargs['api_context']
        return super(BaseTask, self).__call__(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # Optimization hack in heroku instances.
        gc.collect()

    # There are also hooks for retry, fail, and success actions.


class ApiFollower(Task):
    """
    Expects an api context and a result
    """
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

        Only enumeratd modes are acceptable; check the code.  There is a natural rate limit here at 1/s per valve specifications.  There should be a monthly one too.  For lots more docs, see http://dev.dota2.com/showthread.php?t=58317
        """
        try:

            # The steam API accepts a limited set of URLs, and requires a key
            modeDict = {
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

            # If you attempt to access a URL I do not think valve supports, I
            # complain.
            try:
                url = modeDict[mode]
            except KeyError:
                logger.info("Keyerrors on API call!")
                raise
            URL = url + '?' + urlencode(self.api_context.toUrlDict(mode))
            logger.info("URL: " + URL)
            # Exception handling for the URL opening.
            try:
                pageaccess = urllib2.urlopen(URL, timeout=5)
            except urllib2.HTTPError, err:
                if err.code == 104:
                    logger.error(
                        "Got error 104 (connection reset by peer) for mode "
                        + str(mode)
                        + self.api_context.toUrlDict()
                        + ".  Retrying."
                    )
                    self.retry(mode=mode)
                elif err.code == 111:
                    logger.error(
                        "Connection Refused! "
                        + URL
                        + ".  Retrying."
                    )
                    self.retry(mode=mode)
                elif err.code == 404:
                    logger.error("Page not found! " + URL + ".  Retrying.")
                    self.retry(mode=mode)
                elif err.code == 403:
                    logger.error(
                        "Your access was denied. "
                        + URL
                        + ".  Retrying."
                    )
                    self.retry(mode=mode)
                elif err.code == 401:
                    logger.error(
                        "Unauth'd! "
                        + URL
                        + ".  Retrying."
                    )
                    self.retry(mode=mode)
                elif err.code == 500:
                    logger.error("Server Error! " + URL + ".  Retrying.")
                    self.retry(mode=mode)
                elif err.code == 503:
                    logger.error(
                        "Server busy or limit exceeded "
                        + URL
                        + ".  Retrying."
                    )
                    self.retry(mode=mode)
                else:
                    logger.error(
                        "Got error "
                        + str(err)
                        + " with URL "
                        + URL
                        + ".  Retrying."
                    )
                    self.retry(mode=mode)
            except BadStatusLine:
                logger.error(
                    "Bad status line for url %s" % URL
                    + ".  Retrying."
                )
                self.retry(mode=mode)
            except urllib2.URLError as err:
                self.retry(mode=mode)
            except (ssl.SSLError, socket.timeout) as err:
                err = "Connection timeout for {url}. Error: {e}  Retrying."
                logger.error(
                    err.format(
                        url=URL,
                        e=err
                    )
                )
                self.retry(mode=mode)

            # If everything is kosher, import the result and return it.
            data = json.loads(pageaccess.read())
            data['api_context'] = self.api_context
            return data

        except (
            SoftTimeLimitExceeded,
            WorkerLostError,
            TimeLimitExceeded,
        ) as exc:
            try:
                self.retry(mode=mode, exc=exc, countdown=180)

            except MaxRetriesExceededError:
                send_error_email(self.api_context.__str__())
                raise
        except ValueError:
                send_error_email(self.api_context.__str__())
                raise


class CycleApiCall(ApiFollower):
    """
    Recycle an API context to dig deeper into match results.

    Only supports get match history right now, but that is the only API that really leans on repeated calls.
    """

    def run(self, urldata):
        """
        Recursively pings the valve API to get match data and spawns new tasks
        to deal with the downloaded match IDs.
        """
        # Validate
        if self.result['status'] == 15:
            logger.error(
                "Could not pull data. "
                + str(self.api_context.account_id)
                + " disallowed it. "
            )
            p = Player.objects.get(steam_id=self.api_context.account_id)
            p.updated = False
            p.save()
            return True

        elif self.result['status'] == 1:
            # Spawn a bunch of match detail queries

            logger.info("Spawning")

            self.spawnDetailCalls()

            logger.info("Checking for more results")
            if self.moreResultsLeft():
                self.rebound()

            # Successful closeout
            else:
                logger.info("Cleaning up")
                self.cleanup()
            return True
        else:
            logger.error("Unhandled status: "+str(self.result['status']))
            return True

    def spawnDetailCalls(self):
        for result in self.result['matches']:
            self.api_context.processed += 1
            if self.api_context.processed <= self.api_context.matches_desired:

                logger.info(
                    "{0}: {1} done, {2} wanted, doing: {3}".format(
                        self.api_context.account_id,
                        self.api_context.processed,
                        self.api_context.matches_desired,
                        self.api_context.processed <=
                        self.api_context.matches_desired
                    )
                )

                vac = ValveApiCall()
                um = UpdateMatch()
                self.api_context.match_id = result['match_id']
                pass_context = deepcopy(self.api_context)
                chain(vac.s(
                    mode='GetMatchDetails',
                    api_context=pass_context
                ), um.s()).delay()

    def moreResultsLeft(self):
        if not (self.result['results_remaining'] == 0) \
                and self.api_context.processed <= \
                self.api_context.matches_desired:

            logger.info(
                (
                    "Did {0} of {1} for {2}. {3} left.  \n "
                    "Logic: remaining: {4}, "
                    "needing: {5}, in sum: {6}.  Going back"
                ).format(
                    self.api_context.processed,
                    self.api_context.matches_desired,
                    self.api_context.account_id,
                    self.result['results_remaining'],
                    not (self.result['results_remaining'] == 0),
                    self.api_context.processed <=
                        self.api_context.matches_desired,
                    not (self.result['results_remaining'] == 0)
                        and self.api_context.processed <=
                        self.api_context.matches_desired,
                )
            )
            return True

        else:

            logger.info(
                "Did {0} of {1} for {2}. {3} left.  Done.".format(
                    self.api_context.processed,
                    self.api_context.matches_desired,
                    self.api_context.account_id,
                    self.result['results_remaining']
                )
            )

            return False

    # Until the date_max problem is fixed, date_max cannot work.
    def rebound(self):
        logger.info("Rebounding")
        self.api_context.start_at_match_id = self.result[
            'matches'
        ][-1]['match_id']
        self.api_context.date_max = None

        vac = ValveApiCall()
        rpr = CycleApiCall()
        pass_context = deepcopy(self.api_context)
        chain(vac.s(
            mode='GetMatchHistory',
            api_context=pass_context
        ), rpr.s()).delay()

    def cleanup(self):
        # If there is a player we have been focusing on
        if self.api_context.account_id is not None:
            try:
                player = Player.objects.get(
                    steam_id=self.api_context.account_id
                )
                if self.api_context.start_scrape_time:
                    new_last_scrape = self.api_context.start_scrape_time
                else:
                    new_last_scrape = now()
                player.last_scrape_time = new_last_scrape
                player.save()
            except Player.DoesNotExist:
                logger.error(
                    "ERROR! Player does not exist {0}".format(
                        self.api_context.account_id
                    )
                )
