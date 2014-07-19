import gc
import urllib2
import json
import socket
import ssl
from smtplib import SMTP
from itertools import chain as meld
from copy import deepcopy
from time import time as now
from urllib import urlencode
from uuid import uuid4
from celery import Task, chain
from celery.exceptions import (
    SoftTimeLimitExceeded,
    MaxRetriesExceededError,
    TimeLimitExceeded,
    WorkerLostError,
    )
from django.core.files import File
from django.utils.text import slugify
from matches.models import (
    Match,
    LobbyType,
    GameMode,
    LeaverStatus,
    PlayerMatchSummary,
    SkillBuild,
    AdditionalUnit,
    PickBan
)
from django.conf import settings
from datadrivendota.settings.base import STEAM_API_KEY
from players.models import Player, get_tracks
from heroes.models import Ability, Hero
from items.models import Item
from leagues.models import League, LeagueDossier
from guilds.models import Guild
from teams.models import Team, TeamDossier, assemble_pros
from settings.base import ADDER_32_BIT
import logging

### Patch for <urlopen error [Errno -2] Name or service not known in urllib2
import os
os.environ['http_proxy'] = ''
### End Patch

from httplib import BadStatusLine

logger = logging.getLogger(__name__)


class ApiContext(object):
    # Things we send to Valve
    account_id = None
    matches_requested = 100
    skill = 0
    date_max = None
    start_at_match_id = None
    key = None
    match_id = None
    hero_id = None
    # There are magic lists of teh above in the URL constructor.

    # Things we care about internally
    start_scrape_time = now()
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
        elif mode == 'GetMatchHistory':
            valve_URL_vars = [
                'account_id',
                'hero_id',
                'matches_requested',
                'skill',
                'league_id',
                'date_max',
                'date_max',
                'start_at_match_id',
                'key'
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
        ]:
            if hasattr(self, field):
                if getattr(self, field) is not None:
                    strng += "{0}: {1} \n".format(field, getattr(self, field))

        return strng

    def __repr__(self):
        return self.__str__()


# Parents
class BaseTask(Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        self.api_context = kwargs['api_context']
        del kwargs['api_context']
        return super(BaseTask, self).__call__(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
#        logger.info("Ending {task_id}".format(task_id=task_id))
        gc.collect()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # logger.error(
        #     "Task failure! {args}, {kwargs}, {task_id} {einfo}".format(
        #         args=args,
        #         kwargs=kwargs,
        #         task_id=task_id,
        #         einfo=einfo
        #     )
        # )
        pass

    def on_retry(self, exc, id, args, kwargs, einfo):
        # logger.info("Task retry! {args}, {kwargs}, {task_id}".format(
        #     args=args,
        #     kwargs=kwargs,
        #     task_id=id
        # ))
        pass

    def on_success(self, retval, task_id, args, kwargs):
        # logger.info("Task success! {task_id}".format(task_id=task_id))
        pass


class ApiFollower(Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        self.result = args[0].get('result', {})
        self.api_context = args[0].get('api_context', {})
        return super(ApiFollower, self).__call__(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # logger.info("Ending {task_id}".format(task_id=task_id))
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # logger.error(
        #     "Task failure! {args}, {kwargs}, {task_id} {einfo}".format(
        #         args=args,
        #         kwargs=kwargs,
        #         task_id=task_id,
        #         einfo=einfo
        #     )
        # )
        pass

    def on_retry(self, exc, id, args, kwargs, einfo):
        # logger.info(
        #     "Task retry! {args}, {kwargs}, {task_id}".format(
        #         args=args,
        #         kwargs=kwargs,
        #         task_id=id
        #     )
        # )
        pass

    def on_success(self, retval, task_id, args, kwargs):
        # logger.info("Task success! {task_id}".format(task_id=task_id))
        pass


# Descendants
class ValveApiCall(BaseTask):
    def run(self, mode, **kwargs):
        """
        Ping the valve API for downloading results.  Only enumeratd modes are
        acceptable; check the code.  There is a natural rate limit here at 1/s
        per valve specifications.  There should be a monthly one too.
        For lots more docs, see http://dev.dota2.com/showthread.php?t=58317
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
                    'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/'
                ),
                'GetPlayerSummaries': (
                    'https://api.steampowered.com'
                    '/ISteamUser/GetPlayerSummaries/v0002/'
                ),
                'EconomySchema': (
                    'https://api.steampowered.com/IEconItems_570/GetSchema/v0001/'
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
            }

            # If you attempt to access a URL I do not think valve supports, I
            # complain.
            try:
                url = modeDict[mode]
            except KeyError:
                logger.info("Keyerrors!")
                raise
            URL = url + '?' + urlencode(self.api_context.toUrlDict(mode))
            logger.info("URL: " + URL)
            if mode in ['GetMatchHistory', 'GetTeamInfoByTeamID']:
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
                logger.error(
                    "Connection timeout for {url}. Error: {e}  Retrying.".format(
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


class RetrievePlayerRecords(ApiFollower):

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

            #Successful closeout
            else:
                logger.info("Cleaning up")
                self.cleanup()
            return True
        else:
            logger.error("Unhandled status: "+str(self.result['status']))
            return True

    def spawnDetailCalls(self):
        for result in self.result['matches']:
            vac = ValveApiCall()
            um = UploadMatch()
            self.api_context.match_id = result['match_id']
            self.api_context.processed += 1
            pass_context = deepcopy(self.api_context)
            chain(vac.s(
                mode='GetMatchDetails',
                api_context=pass_context
            ), um.s()).delay()

    def moreResultsLeft(self):
        return not self.result['results_remaining'] == 0
        #Until the date_max problem is fixed, rebounding cannot work.

    def rebound(self):
        logger.info("Rebounding")
        self.api_context.start_at_match_id = self.result[
            'matches'
        ][-1]['match_id']
        self.api_context.date_max = None

        # if self.api_context.date_pull is False:
            # self.api_context.start_at_match_id = self.result[
            #     'matches'
            # ][-1]['match_id']
            # self.api_context.date_max = None
        # else:
        #     # If we want to poll more than 500 results deep, we reset the
        #     # valve api's date bounding
        #     self.api_context.date_max = self.result[
        #         'matches'
        #         ][-1]['start_time']
        #     self.api_context.start_at_match_id = None
        #     self.api_context.date_pull = False

        vac = ValveApiCall()
        rpr = RetrievePlayerRecords()
        pass_context = deepcopy(self.api_context)
        chain(vac.s(
            mode='GetMatchHistory',
            api_context=pass_context
        ), rpr.s()).delay()

    def cleanup(self):
        #If there is a player we have been focusing on
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


class UploadMatch(ApiFollower):

    def run(self, data):
        """
        Uploads a match given the return of an API call.
        Only if the match does not exist are the player summaries imported;
        this will not correctly account for players that unanonymize their
        data. More code to the effect of "Look in the hero slot of the player
        you are searching for, see if it is anonymous, update if so" is
        needed; if urldata['status'] == 1: right now this just trawls for
        overall match data.
        """
        data = self.result

        kwargs = {
            'radiant_win': data['radiant_win'],
            'duration': data['duration'],
            'start_time': data['start_time'],
            'steam_id': data['match_id'],
            'match_seq_num': data['match_seq_num'],
            'tower_status_radiant': data['tower_status_radiant'],
            'tower_status_dire': data['tower_status_dire'],
            'barracks_status_radiant': data['barracks_status_radiant'],
            'barracks_status_dire': data['barracks_status_dire'],
            'cluster': data['cluster'],
            'first_blood_time': data['first_blood_time'],
            'lobby_type': LobbyType.objects.get_or_create(
                steam_id=data['lobby_type']
            )[0],
            'human_players': data['human_players'],
            'positive_votes': data['positive_votes'],
            'negative_votes': data['negative_votes'],
            'game_mode': GameMode.objects.get_or_create(
                steam_id=data['game_mode']
            )[0],
            'skill': self.api_context.skill,
        }
        try:

            league = League.objects.get_or_create(
                steam_id=data['leagueid']
                )[0]
            kwargs.update({'league': league})
        except KeyError:
            pass

        update = False
        try:
            match = Match.objects.get(steam_id=data['match_id'])
            if self.api_context.refresh_records:
                for key, value in kwargs.iteritems():
                    setattr(match, key, value)
                match.save()
                upload_match_summary(
                    players=data['players'],
                    parent_match=match,
                    refresh_records=self.api_context.refresh_records
                )
                update = True

        except Match.DoesNotExist:
            update = True
            match = Match.objects.create(**kwargs)
            match.save()
            upload_match_summary(
                players=data['players'],
                parent_match=match,
                refresh_records=self.api_context.refresh_records
            )

        if 'picks_bans' in data.keys() and update:
            for pickban in data['picks_bans']:
                datadict = {
                    'match': match,
                    'is_pick': pickban['is_pick'],
                    'hero': Hero.objects.get_or_create(
                        steam_id=pickban['hero_id']
                    )[0],
                    'team': pickban['team'],
                    'order': pickban['order'],

                }
                pb = PickBan.objects.get_or_create(
                    match=match,
                    order=pickban['order'],
                    defaults=datadict
                )[0]
                pb.save()

        if 'series_id' in data.keys() and update:
            match.series_id = data['series_id']

        if 'series_type' in data.keys() and update:
            match.series_type = data['series_type']

        if 'radiant_guild_id' in data.keys() and update:
            datadict = {
                'steam_id': data["radiant_guild_id"],
                'name': data["radiant_guild_name"],
                'logo': data["radiant_guild_logo"],
            }
            g = Guild.objects.get_or_create(
                steam_id=data["radiant_guild_id"],
                defaults=datadict
            )[0]
            match.radiant_guild = g

        if 'dire_guild_id' in data.keys() and update:
            datadict = {
                'steam_id': data["dire_guild_id"],
                'name': data["dire_guild_name"],
                'logo': data["dire_guild_logo"],
            }
            g = Guild.objects.get_or_create(
                steam_id=data["dire_guild_id"],
                defaults=datadict
            )[0]
            match.dire_guild = g

        if 'radiant_team_id' in data.keys() and update:
            radiant_team = Team.objects.get_or_create(
                steam_id=data['radiant_team_id']
                )[0]
            match.radiant_team = radiant_team
            match.radiant_team_complete = True \
                if data['radiant_team_id'] == 1 else False

        if 'dire_team_id' in data.keys() and update:
            dire_team = Team.objects.get_or_create(
                steam_id=data['dire_team_id']
                )[0]
            match.dire_team = dire_team
            match.dire_team_complete = True \
                if data['dire_team_id'] == 1 else False
        match.save()


class RefreshUpdatePlayerPersonas(BaseTask):

    def run(self):
        """
        Go through the users for whom update is True and group them into lists
        of 50.  The profile update API actually supports up to 100
        """
        list_send_length = 50
        users = Player.objects.filter(updated=True)
        tracked = get_tracks(users)

        teams = TeamDossier.objects.all()
        pros = assemble_pros(teams)

        track_list = meld(users, tracked)

        check_list = [user.steam_id for user in track_list].extend(pros)
        querylist = []

        for counter, user in enumerate(check_list, start=1):
            id_64_bit = str(user + ADDER_32_BIT)
            querylist.append(id_64_bit)

            # if our list is list_send_length long or we have reached the end
            if counter % list_send_length == 0 or counter == len(check_list):
                steamids = ",".join(querylist)
                vac = ValveApiCall()
                upp = UpdatePlayerPersonas()
                self.api_context.steamids = steamids
                pass_context = deepcopy(self.api_context)
                chain(vac.s(
                    mode='GetPlayerSummaries',
                    api_context=pass_context
                ), upp.s()).delay()
                querylist = []


class UpdatePlayerPersonas(ApiFollower):

    def run(self, urldata):
        """Make the avatar and persona facts of a profile match current."""
        #This options is present in the return code, but not needed here.
        #valveOpts = urldata['valveOpts']
        response = urldata['response']

        for pulled_player in response['players']:
            logger.info(
                "Updating "
                + pulled_player['personaname']
                + ","
                + str(pulled_player['steamid'])
            )
            # The PlayerSummaries call returns 64 bit ids.  It is super
            # annoying.
            id_32bit = int(pulled_player['steamid']) % ADDER_32_BIT

            player, created = Player.objects.get_or_create(steam_id=id_32bit)
            player.persona_name = pulled_player['personaname']
            player.profile_url = pulled_player['profileurl']
            player.avatar = pulled_player['avatar']
            player.avatar_medium = pulled_player['avatarmedium']
            player.avatar_full = pulled_player['avatarfull']
            player.save()


class RefreshPlayerMatchDetail(BaseTask):

    def run(self):
        """
        Go through the users for whom update is True and pull match histories
        since their last scrape time
        """
        users = Player.objects.filter(updated=True).select_related()
        tracked = get_tracks(users)
        check_list = meld(users, tracked)
        check_list = [user for user in check_list]
        for counter, user in enumerate(check_list, start=1):
            context = ApiContext()
            context.account_id = user.steam_id

            if self.api_context.matches_requested is None:
                context.matches_requested = 20
            else:
                context.matches_requested = self.api_context.matches_requested

            if self.api_context.matches_desired is None:
                context.matches_desired = 20
            else:
                context.matches_desired = self.api_context.matches_desired

            context.deepcopy = True
            context.start_scrape_time = now()
            context.last_scrape_time = user.last_scrape_time
            logger.info(context)
            vac = ValveApiCall()
            rpr = RetrievePlayerRecords()
            chain(vac.s(
                mode='GetMatchHistory',
                api_context=context
            ), rpr.s()).delay()


class AcquirePlayerData(BaseTask):

    def run(self):
        if self.api_context.account_id is None:
            logger.error("Needed an account id, had none, failed.")
        player = Player.objects.get_or_create(
            steam_id=self.api_context.account_id
        )[0]
        player.updated = True
        player.save()
        if self.api_context.matches_requested is None:
            self.api_context.matches_requested = 500
        self.api_context.start_scrape_time = now()
        self.api_context.last_scrape_time = player.last_scrape_time
        self.api_context.deepycopy = True
        if self.api_context.matches_desired is None:
            self.api_context.matches_desired = 500
        for skill in self.api_context.skill_levels:
            self.api_context.skill = skill

            vac = ValveApiCall()
            rpr = RetrievePlayerRecords()
            pass_context = deepcopy(self.api_context)
            chain(vac.s(
                mode='GetMatchHistory',
                api_context=pass_context
            ), rpr.s()).delay()


class AcquireHeroSkillData(BaseTask):

    def run(self):
        if (
                self.api_context.account_id is not None
                or self.api_context.hero_id is None
                ):
            logger.error(
                "Not allowed to have an account_id for this, and need a Hero."
            )
        else:

            if self.api_context.matches_requested is None:
                self.api_context.matches_requested = 100
            self.api_context.deepcopy = False
            if self.api_context.matches_desired is None:
                self.api_context.matches_desired = 100
            self.api_context.skill_levels = [1, 2, 3]
            for skill in self.api_context.skill_levels:
                self.api_context.skill = skill
                vac = ValveApiCall()
                rpr = RetrievePlayerRecords()
                pass_context = deepcopy(self.api_context)
                chain(vac.s(
                    mode='GetMatchHistory',
                    api_context=pass_context
                ), rpr.s()).delay()
            logger.info("Done")


class AcquireMatches(Task):

    def run(self, matches=[]):
        for match in matches:
            logger.info("Requesting match {0}".format(match))
            c = ApiContext()
            c.matches_requested = 1
            c.matches_desired = 1
            c.refresh_records = True
            c.match_id = match
            c.refresh_records = True
            vac = ValveApiCall()
            um = UploadMatch()
            c = chain(vac.s(api_context=c, mode='GetMatchDetails'), um.s())
            c.delay()


class AcquireTeams(Task):

    def run(self):
        matches = Match.objects.filter(skill=4).exclude(radiant_team=None)\
            .select_related('radiant_team__steam_id')
        teams = [m.radiant_team.steam_id for m in matches]

        matches = Match.objects.filter(skill=4).exclude(dire_team=None)\
            .select_related('dire_team__steam_id')
        teams.extend([m.dire_team.steam_id for m in matches])
        teams = list(set(teams))
        for t in teams:
            c = ApiContext()
            c.refresh_records = True
            c.start_at_team_id = t
            c.teams_requested = 1
            vac = ValveApiCall()
            ul = UploadTeam()
            c = chain(vac.s(api_context=c, mode='GetTeamInfoByTeamID'), ul.s())
            c.delay()


class AcquireTeamDossiers(Task):

    def run(self):
        teams = Team.objects.filter(teamdossier=None)
        for t in teams:
            c = ApiContext()
            c.refresh_records = True
            c.start_at_team_id = t.steam_id
            c.teams_requested = 1
            vac = ValveApiCall()
            ul = UploadTeam()
            c = chain(vac.s(api_context=c, mode='GetTeamInfoByTeamID'), ul.s())
            c.delay()


class UploadTeam(ApiFollower):
    def run(self, urldata):
        for team in self.result['teams']:
            t, created = Team.objects.get_or_create(
                steam_id=team['team_id']
                )
            try:
                teamdoss = TeamDossier.objects.get(
                    team=t,
                    )
                if self.api_context.refresh_records:
                    mapping_dict = {
                        'name': 'name',
                        'tag': 'tag',
                        'created': 'time_created',
                        'logo': 'logo',
                        'logo_sponsor': 'logo_sponsor',
                        'country_code': 'country_code',
                        'url': 'url',
                        'games_played_with_current_roster': 'games_played_with_current_roster',
                    }
                    for internal, external in mapping_dict.iteritems():
                        if external in team.iterkeys():
                            setattr(teamdoss, internal, team.get(external))

                    map_team_players(teamdoss, team)
                    teamdoss.save()

                    update_team_logos(t)

                    # c = ApiContext()
                    # utl = UpdateTeamLogos()
                    # utl.s(api_context=c, team_steam_id=t.steam_id).delay()

            except TeamDossier.DoesNotExist:
                teamdoss = TeamDossier.objects.create(
                    team=t,
                    name=team['name'],
                    tag=team['tag'],
                    created=team['time_created'],
                    logo_sponsor=team['logo_sponsor'],
                    logo=team['logo'],
                    country_code=team['country_code'],
                    url=team['url'],
                    games_played_with_current_roster=team[
                        'games_played_with_current_roster'
                    ],
                    )
                map_team_players(teamdoss, team)
                if 'rating' in team.iterkeys():
                        setattr(teamdoss, 'rating', team.get('rating'))

                teamdoss.save()
                update_team_logos(t)


class UpdateTeamLogo(ApiFollower):
    def run(self, urldata):
        team = Team.objects.get(steam_id=self.api_context.team_id)
        URL = urldata['data']['url']
        try:
            imgdata = urllib2.urlopen(URL, timeout=5)
            with open('%s.png' % str(uuid4()), 'w+') as f:
                f.write(imgdata.read())
            filename = slugify(team.teamdossier.name) + '.png'
            if self.api_context.logo_type == 'team':
                team.teamdossier.logo_image.save(
                    filename, File(open(f.name))
                    )
            else:
                team.teamdossier.logo_sponsor_image.save(
                    filename, File(open(f.name))
                )
            os.remove(f.name)

        # If we fail, put in a placeholder and freak.
        except Exception:
                filename = slugify(team.teamdossier.name)+'_logo.png'
                URL = ('https://s3.amazonaws.com/datadrivendota'
                       '/images/blank-logo.png')
                imgdata = urllib2.urlopen(URL, timeout=5)
                with open('%s.png' % str(uuid4()), 'w+') as f:
                    f.write(imgdata.read())

                if self.api_context.logo_type == 'team':
                    team.teamdossier.logo_image.save(
                        filename, File(open(f.name))
                        )
                else:
                    team.teamdossier.logo_sponsor_image.save(
                        filename, File(open(f.name))
                    )
                os.remove(f.name)
                raise


class AcquireLeagues(Task):

    def run(self):
        c = ApiContext()
        c.refresh_records = True
        vac = ValveApiCall()
        ul = UploadLeague()
        c = chain(vac.s(api_context=c, mode='GetLeagueListing'), ul.s())
        c.delay()


class UploadLeague(ApiFollower):
    def run(self, urldata):
        for league in self.result['leagues']:
            l, created = League.objects.get_or_create(
                steam_id=league['leagueid']
                )
            try:
                ldoss = LeagueDossier.objects.get(
                    league=l,
                    )
            except LeagueDossier.DoesNotExist:
                ldoss = LeagueDossier.objects.create(
                    league=l,
                    name=league['name'],
                    description=league['description'],
                    tournament_url=league['tournament_url'],
                    item_def=league['itemdef']
                    )


class UpdateLeagueGames(Task):
    """Pulls in all games for all extant leagues"""

    def run(self):
        for league in League.objects.all():
            c = ApiContext()
            c.league_id = league.steam_id
            c.matches_requested = 500
            c.matches_desired = 500
            c.skill = 4
            vac = ValveApiCall()
            rpr = RetrievePlayerRecords()
            c = chain(vac.s(api_context=c, mode='GetMatchHistory'), rpr.s())
            c.delay()


class MirrorLeagueLogos(Task):
    """Annexes the url data for league logos from the item schema and updates the leaguedossier objects"""

    def run(self):
        c = ApiContext()
        vac = ValveApiCall()
        ull = UpdateLeagueLogos()
        c = chain(vac.s(api_context=c, mode='GetSchema'), ull.s())
        c.delay()


class UpdateLeagueLogos(ApiFollower):
    """ Takes a given schema result and annexes logo urls."""

    def run(self, urldata):
        leagues = LeagueDossier.objects.all()
        data = self.result['items']
        mapping = {d['defindex']: d['image_url'] for d in data}
        blank_URL = 'http://s3.amazonaws.com/datadrivendota/images/blank-logo.png'
        for leaguedossier in leagues:
            filename = slugify(leaguedossier.name)+'.png'
            try:
                url = mapping[leaguedossier.item_def]
                if url != '':
                    imgdata = urllib2.urlopen(url, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())
                    leaguedossier.logo_image.save(
                        filename, File(open(f.name))
                    )
                    os.remove(f.name)
                else:
                    imgdata = urllib2.urlopen(blank_URL, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())

                    leaguedossier.logo_image.save(
                        filename, File(open(f.name))
                        )
                    os.remove(f.name)

            except (urllib2.URLError, ssl.SSLError, socket.timeout):
                self.retry()
            except (KeyError):
                if leaguedossier.logo_image is None:
                    imgdata = urllib2.urlopen(blank_URL, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())

                    leaguedossier.logo_image.save(
                        filename, File(open(f.name))
                        )
                    os.remove(f.name)


class MirrorProNames(Task):
    """Gets the pro name for each person in the current roster set"""

    def run(self):
        teams = TeamDossier.objects.all()
        pros = assemble_pros(teams)
        for p in pros:
            c = ApiContext()
            vac = ValveApiCall()
            c.AccountID = p
            upn = UpdateProNames()
            t = chain(
                vac.s(api_context=c, mode='GetPlayerOfficialInfo'), upn.s()
            )
            t.delay()


class UpdateProNames(ApiFollower):
    """Takes a ping to the official player database and updates that player's pro name"""
    def run(self, urldata):
        player = Player.objects.get_or_create(
            steam_id=self.api_context.AccountID
            )[0]
        if self.result['Name'] == '':
            player.pro_name = None
            player.save()
        else:
            tag = self.result['TeamTag']
            name = self.result['Name']
            player.pro_name = '[' + tag + '] ' + name
            player.save()


class AcquireHiddenLeagueGames(Task):
    """Gets the pro name for each person in the current roster set"""

    def run(self, league_id):
        lst = [
            '101495620',  # Alliance
            '94362277',  # Titan
            '87276347',  # EG
            '100317750',  # Fnatic
            '100883708',  # Newbee
            '91698091',  # Vici
            '70388657',  # Na'Vi
            '90892734',  # DK
            '88553213',  # iG
            '19757254',  # Cloud 9
            '89269794',  # Empire
            '1185644',  # Na'Vi US
            '131380551',  # Arrow
            '123854991',  # LGD
            '87285329',  # mouz
            '86738694',  # Liquid
            '88933594',  # MVP
            '21289303',  # CIS
            '36547811',  # VP
        ]
        for acct in lst:
            c = ApiContext()
            vac = ValveApiCall()
            c.account_id = acct
            c.league_id = league_id
            rhgr = RetrieveHiddenGameResults()
            t = chain(
                vac.s(api_context=c, mode='GetTournamentPlayerStats'), rhgr.s()
            )
            t.delay()


class RetrieveHiddenGameResults(ApiFollower):
    """"""
    def run(self, urldata):
        matches = [match['match_id'] for match in urldata['result']['matches']]
        print matches
        am = AcquireMatches()
        am.delay(matches=matches)


def upload_match_summary(players, parent_match, refresh_records):
    """
    Populates the endgame summary data that is associated with a match
    and invokes the build parser.  This needs to be fixed for players that
    unanonymize by checking on hero_slot, ignoring player, and updating
    if new data has been included (in particular, which player we are
    talking about).
    """
    for player in players:
        # Bots do not have data assigned to them.  We have a fictitious
        # player and leaver status to hold this data.
        try:
            account_id = player['account_id']
            leaver_status = player['leaver_status']
        except KeyError:
            account_id = 0  # No acct ID means the player is a bot.
            leaver_status = -1
        kwargs = {
            'match': parent_match,
            'player': Player.objects.get_or_create(
                steam_id=account_id)[0],
            'leaver': LeaverStatus.objects.get_or_create(
                steam_id=leaver_status)[0],
            'player_slot': player['player_slot'],
            'hero': Hero.objects.get_or_create(
                steam_id=player['hero_id'],
                )[0],
            'item_0': Item.objects.get_or_create(steam_id=player['item_0'])[0],
            'item_1': Item.objects.get_or_create(steam_id=player['item_1'])[0],
            'item_2': Item.objects.get_or_create(steam_id=player['item_2'])[0],
            'item_3': Item.objects.get_or_create(steam_id=player['item_3'])[0],
            'item_4': Item.objects.get_or_create(steam_id=player['item_4'])[0],
            'item_5': Item.objects.get_or_create(steam_id=player['item_5'])[0],
            'kills': player['kills'],
            'deaths': player['deaths'],
            'assists': player['assists'],
            'gold': player['gold'],
            'last_hits': player['last_hits'],
            'denies': player['denies'],
            'gold_per_min': player['gold_per_min'],
            'xp_per_min': player['xp_per_min'],
            'gold_spent': player['gold_spent'],
            'hero_damage': player['hero_damage'],
            'tower_damage': player['tower_damage'],
            'hero_healing': player['hero_healing'],
            'level': player['level'],
        }
        try:
            pms = PlayerMatchSummary.objects.get(
                player_slot=player['player_slot'],
                match=parent_match
            )
            if refresh_records:
                for key, value in kwargs.iteritems():
                    setattr(pms, key, value)
                pms.save()
            playermatchsummary = pms
        except PlayerMatchSummary.DoesNotExist:
            playermatchsummary = PlayerMatchSummary.objects.get_or_create(
                **kwargs
            )[0]

        if 'ability_upgrades' in player.keys():
            for skillpick in player['ability_upgrades']:
                kwargs = {
                    'player_match_summary': playermatchsummary,
                    'ability': Ability.objects.get_or_create(
                        steam_id=skillpick['ability']
                    )[0],
                    'time': skillpick['time'],
                    'level': skillpick['level'],
                }
                SkillBuild.objects.get_or_create(**kwargs)

        if 'additional_units' in player.keys():
            for unit in player['additional_units']:
                kwargs = {
                    'player_match_summary': playermatchsummary,
                    'unit_name': unit['unitname'],
                    'item_0': Item.objects.get_or_create(
                        steam_id=unit['item_0']
                    )[0],
                    'item_1': Item.objects.get_or_create(
                        steam_id=unit['item_1']
                    )[0],
                    'item_2': Item.objects.get_or_create(
                        steam_id=unit['item_2']
                    )[0],
                    'item_3': Item.objects.get_or_create(
                        steam_id=unit['item_3']
                    )[0],
                    'item_4': Item.objects.get_or_create(
                        steam_id=unit['item_4']
                    )[0],
                    'item_5': Item.objects.get_or_create(
                        steam_id=unit['item_5']
                    )[0],
                }
                AdditionalUnit.objects.get_or_create(**kwargs)


def map_team_players(teamdoss, team):
    player_field_mapping_dict = {
        'player_0': 'player_0_account_id',
        'player_1': 'player_1_account_id',
        'player_2': 'player_2_account_id',
        'player_3': 'player_3_account_id',
        'player_4': 'player_4_account_id',
        'admin': 'admin_account_id',
    }
    for internal, external in player_field_mapping_dict.iteritems():
        if external in team.iterkeys():
            p = Player.objects.get_or_create(steam_id=team.get(external))[0]
            setattr(teamdoss, internal, p)


# def get_logo_image(logo, team, suffix):
#         mode = 'GetUGCFileDetails'
#         c = ApiContext()
#         c.ugcid = logo
#         URL = ('http://api.steampowered.com/ISteamRemoteStorage/'
#                'GetUGCFileDetails/v1/?appid=570&') + \
#             urlencode(c.toUrlDict(mode))
#         logger.info("URL: {0}".format(URL))
#         try:
#             pageaccess = urllib2.urlopen(URL, timeout=5)
#             data = json.loads(pageaccess.read())['data']
#             URL = data['url']
#         except urllib2.HTTPError as err:
#             logger.error("{0} for {1}".format(err.code, URL))

#         try:
#             imgdata = urllib2.urlopen(URL, timeout=5)
#             with open('%s.png' % str(uuid4()), 'w+') as f:
#                 f.write(imgdata.read())
#             filename = slugify(team.teamdossier.name)+suffix
#             return filename, f
#         except urllib2.HTTPError as err:
#             logger.error("{0} for {1}".format(err.code, URL))


def send_error_email(body):
    smtp = SMTP()
    debuglevel = 0
    smtp.set_debuglevel(debuglevel)
    smtp.connect(settings.EMAIL_HOST, settings.EMAIL_PORT)

    smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    message_text = "Error! Failed with context:\n{0}\n\nBye\n".format(body)
    from_addr = "celery@datadrivendota.com"
    to_addr = "ben@datadrivendota.com"
    subj = 'Error!'
    msg = "From: {0}\nTo: {1}\nSubject: {2}\n\n{3}".format(
        from_addr, to_addr, subj, message_text
    )

    smtp.sendmail(from_addr, to_addr, msg)
    smtp.quit()


def update_team_logos(team):
    #Refresh the logo
    logo = team.teamdossier.logo
    teamdoss = team.teamdossier
    if logo != 0 and logo is not None:
        c = ApiContext()
        vac = ValveApiCall()
        c.ugcid = teamdoss.logo
        c.team_id = teamdoss.team.steam_id
        c.logo_type = 'team'

        utl = UpdateTeamLogo()

        c = chain(
            vac.s(api_context=c, mode='GetUGCFileDetails'), utl.s()
        )
        c.delay()

    logo = team.teamdossier.logo_sponsor
    if logo != 0 and logo is not None:
        c = ApiContext()
        vac = ValveApiCall()
        c.ugcid = teamdoss.logo
        c.team_id = teamdoss.team.steam_id
        c.logo_type = 'sponsor'

        utl = UpdateTeamLogo()

        c = chain(
            vac.s(api_context=c, mode='GetUGCFileDetails'), utl.s()
        )
        c.delay()
