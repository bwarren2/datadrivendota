import urllib2
import json
import socket
import ssl
from itertools import chain as meld
from copy import deepcopy
from time import time as now
from urllib import urlencode
from matches.models import Match, LobbyType, GameMode,\
 LeaverStatus, PlayerMatchSummary, SkillBuild
from datadrivendota.settings.base import STEAM_API_KEY
from players.models import Player, get_tracks
from heroes.models import Ability, Hero
from settings.base import ADDER_32_BIT
from celery import Task, chain
from celery.registry import tasks
import logging

### Patch for <urlopen error [Errno -2] Name or service not known in urllib2
import os
os.environ['http_proxy']=''
### End Patch

from httplib import BadStatusLine

logger = logging.getLogger(__name__)

class ApiContext(object):
    #Things we send to Valve
    account_id=None
    matches_requested=100
    skill=0
    date_max=None
    start_at_match_id=None
    key=None
    match_id=None
    hero_id=None
    #There are magic lists of teh above in the URL constructor.

    #Things we care about internally
    start_scrape_time=now()
    matches_desired=None
    skill_levels=[0]  #This only works for heroes.
    deepcopy=False
    last_scrape_time=0
    steamids = None
    processed=0
    refresh_records = False

    def toUrlDict(self, mode):
        if mode == 'GetPlayerSummaries':
            valve_URL_vars=['steamids','key']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetMatchDetails':
            valve_URL_vars=['match_id','key']
            return self.dictVars(valve_URL_vars)
        elif mode == 'GetMatchHistory':
            valve_URL_vars=['account_id','hero_id','matches_requested',
            'skill','date_max','date_max','start_at_match_id','key']
            return self.dictVars(valve_URL_vars)
        else:
            logger.error("I did not understand mode: "+mode)

    def dictVars(self, url_vars):
        return_dict={}
        for var in url_vars:
            if getattr(self,var,None) is not None:
                return_dict[var]=getattr(self,var)
        return return_dict


    def __str__(self):
        strng =  "Acct id: "+str(self.account_id)+"\n"
        strng += "matches requested: "+str(self.matches_requested)+"\n"
        strng += "Skill: "+str(self.skill)+"\n"
        strng += "date max: "+str(self.date_max)+"\n"
        strng += "start_at_match_id: "+str(self.start_at_match_id)+"\n"
        strng += "key: "+str(self.key)+"\n"

        #Things we care about internally
        strng += "start scrape time: "+str(self.start_scrape_time)+"\n"
        strng += "matches desired: "+str(self.matches_desired)+"\n"
        strng += "skill_levels: "+str(self.skill_levels)+"\n"
        strng += "deepcopy: "+str(self.deepcopy)+"\n"
        strng += "last scrape time: "+str(self.last_scrape_time)+"\n"
        return strng


#Parents
class BaseTask(Task):

    abstract=True
    def __call__(self, *args, **kwargs):
        #logger.info("Starting to run")
        self.api_context = kwargs['api_context']
        del kwargs['api_context']
        return super(BaseTask, self).__call__(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        logger.info("Ending {task_id}".format(task_id=task_id))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error("Task failure! {args}, {kwargs}, {task_id} {einfo}".format(
            args=args,kwargs=kwargs,task_id=task_id,einfo=einfo))

    def on_retry(self, exc, id, args, kwargs, einfo):
        logger.info("Task retry! {args}, {kwargs}, {task_id}".format(
            args=args,kwargs=kwargs,task_id=id))

    def on_success(self, retval, task_id, args, kwargs):
        logger.info("Task success! {task_id}".format(task_id=task_id))

class ApiFollower(Task):

    abstract=True
    def __call__(self, *args, **kwargs):
        self.result = args[0].get('result',{})
        self.api_context = args[0].get('api_context',{})
        return super(ApiFollower, self).__call__(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        logger.info("Ending {task_id}".format(task_id=task_id))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error("Task failure! {args}, {kwargs}, {task_id} {einfo}".format(
            args=args,kwargs=kwargs,task_id=task_id,einfo=einfo))

    def on_retry(self, exc, id, args, kwargs, einfo):
        logger.info("Task retry! {args}, {kwargs}, {task_id}".format(
            args=args,kwargs=kwargs,task_id=id))

    def on_success(self, retval, task_id, args, kwargs):
        logger.info("Task success! {task_id}".format(task_id=task_id))


#Descendants
class ValveApiCall(BaseTask):
    def run(self, mode, **kwargs):
        """ Ping the valve API for downloading results.  Only enumeratd modes are
        acceptable; check the code.  There is a natural rate limit here at 1/s
        per valve specifications.  There should be a monthly one too.
        For lots more docs, see http://dev.dota2.com/showthread.php?t=58317 """
        # The steam API accepts a limited set of URLs, and requires a key
        self.api_context.key = STEAM_API_KEY
        modeDict = {'GetMatchHistory':              'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v001/',
                    'GetMatchDetails':              'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v001/',
                    'GetHeroes':                    'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/',
                    'GetPlayerSummaries':           'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/',
                    'EconomySchema':                'https://api.steampowered.com/IEconItems_570/GetSchema/v0001/',
                    'GetLeagueListing':             'https://api.steampowered.com/IDOTA2Match_570/GetLeagueListing/v0001/',
                    'GetLiveLeagueGames':           'https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v0001/',
                    'GetMatchHistoryBySequenceNum': 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistoryBySequenceNum/v0001/',
                    'GetTeamInfoByTeamID':          'https://api.steampowered.com/IDOTA2Match_570/GetTeamInfoByTeamID/v001/',
                    }

        # If you attempt to access a URL I do not think valve supports, I complain.
        try:
            url = modeDict[mode]
        except KeyError:
            logger.info("Keyerrors!")

        URL = url + '?' + urlencode(self.api_context.toUrlDict(mode))
        logger.info("URL: "+ URL)
        # Exception handling for the URL opening.
        try:
            pageaccess = urllib2.urlopen(URL, timeout=5)
        except urllib2.HTTPError, err:
            if err.code == 104:
                logger.error("Got error 104 (connection reset by peer) for mode " + str(mode) + self.api_context.toUrlDict() + ".  Retrying.")
                self.retry(mode=mode)
            elif err.code == 111:
                logger.error("Connection Refused! "+URL+ ".  Retrying.")
                self.retry(mode=mode)
            elif err.code == 404:
                logger.error("Page not found! "+URL+ ".  Retrying.")
                self.retry(mode=mode)
            elif err.code == 403:
                logger.error("Your access was denied. "+URL+ ".  Retrying.")
                self.retry(mode=mode)
            elif err.code == 401:
                logger.error("Unauth'd! "+URL+ ".  Retrying.")
                self.retry(mode=mode)
            elif err.code == 500:
                logger.error("Server Error! "+URL+ ".  Retrying.")
                self.retry(mode=mode)
            elif err.code == 503:
                logger.error("Server busy or limit exceeded "+URL+ ".  Retrying.")
                self.retry(mode=mode)
            else:
                logger.error("Got error "+str(err)+" with URL "+URL+ ".  Retrying.")
                self.retry(mode=mode)
        except BadStatusLine:
            logger.error("Bad status line for url %s" % URL+ ".  Retrying.")
            self.retry(mode=mode)
        except urllib2.URLError as err:
            self.retry(mode=mode)
        except (ssl.SSLError, socket.timeout) as err:
            logger.error("Connection timeout for {url}. Error: {e}  Retrying.".format(url=URL,e=err))
            self.retry(mode=mode)



        # If everything is kosher, import the result and return it.
        data = json.loads(pageaccess.read())
        # Append the options given so we can tell what the invocation was.
        # For example, it is not straightforward to deduce the calling account_id
        # unless you do this.
        data['api_context'] = self.api_context
        return data
tasks.register(ValveApiCall)


class RetrievePlayerRecords(ApiFollower):

    def run(self, urldata):
        """
        Recursively pings the valve API to get match data and spawns new tasks
        to deal with the downloaded match IDs.
        """
        try:
        #Validate
            if self.result['status'] == 15:
                logger.error("Could not pull data. "+str(self.api_context.account_id)+" disallowed it. ")
                p = Player.objects.get(steam_id=self.api_context.account_id)
                p.updated=False
                p.save()
                return True
            elif self.result['status'] == 1:
                #Spawn a bunch of match detail queries

                logger.info("Spawning")
                self.spawnDetailCalls()
                #Go around again if there are more records and the last one was before last scrape.
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
        except Exception, err:
            logger.error("ERROR!:{0}".format(err))
            return False

    def rebound(self):
        logger.info("Rebounding")
        self.api_context.start_at_match_id = self.result['matches'][-1]['match_id']
        # If we want to poll more than 500 results deep, we need to reset the
        # valve api's date bounding
        if self.api_context.deepcopy==True:
            self.api_context.date_max = self.result['matches'][-1]['start_time']
        vac = ValveApiCall()
        rpr = RetrievePlayerRecords()
        pass_context = deepcopy(self.api_context)
        chain(vac.s(mode='GetMatchHistory',api_context=pass_context), rpr.s()).delay()


    def cleanup(self):
        try:
            player = Player.objects.get(steam_id=self.api_context.account_id)
            new_last_scrape = self.api_context.start_scrape_time if self.api_context.start_scrape_time else now()
            player.last_scrape_time = new_last_scrape
            player.save()
        except Player.DoesNotExist:
            logger.error("ERROR! Player does not exist {0}".format(self.api_context.account_id))

    def spawnDetailCalls(self):
        for result in self.result['matches']:
            vac = ValveApiCall()
            um = UploadMatch()
            self.api_context.match_id=result['match_id']
            self.api_context.processed+=1
            pass_context = deepcopy(self.api_context)
            chain(vac.s(mode='GetMatchDetails',api_context=pass_context), um.s()).delay()

    def moreResultsLeft(self):
        if self.result['results_remaining'] == 0:
            return False
        elif self.api_context.processed >= self.api_context.matches_desired:
            return False
        else:
            if self.api_context.deepcopy is False:
                return self.api_context.last_scrape_time < self.result['matches'][-1]['start_time']
            else:
                return True

tasks.register(RetrievePlayerRecords)


class UploadMatch(ApiFollower):

    def run(self, data):
        """
        Uploads a match given the return of an API call.
        Only if the match does not exist are the player summaries imported;
        this will not correctly account for players that unanonymize their data.
        More code to the effect of "Look in the hero slot of the player you are
        searching for, see if it is anonymous, update if so" is needed;
        if urldata['status'] == 1:
        right now this just trawls for overall match data.
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
            'lobby_type': LobbyType.objects.get_or_create(steam_id=data['lobby_type'])[0],
            'human_players': data['human_players'],
            'league_id': data['leagueid'],
            'positive_votes': data['positive_votes'],
            'negative_votes': data['negative_votes'],
            'game_mode': GameMode.objects.get_or_create(steam_id=data['game_mode'])[0],
            'skill': self.api_context.skill,
        }

        try:
            match = Match.objects.get(steam_id=data['match_id'])
            if self.api_context.refresh_records:
                for key, value in kwargs.iteritems():
                    setattr(match,key,value)
                match.save()
                upload_match_summary(players=data['players'], parent_match=match,refresh_records=self.api_context.refresh_records)

        except Match.DoesNotExist:
            match = Match.objects.create(**kwargs)
            match.save()
            upload_match_summary(players=data['players'], parent_match=match,refresh_records=self.api_context.refresh_records)
tasks.register(UploadMatch)


class RefreshUpdatePlayerPersonas(BaseTask):

    def run(self):
        """ Go through the users for whom update is True and group them into lists
        of 50.  The profile update API actually supports up to 100"""
        list_send_length = 50
        users = Player.objects.filter(updated=True)
        tracked = get_tracks(users)
        check_list = meld(users,tracked)
        check_list = [user for user in check_list]
        querylist = []

        for counter, user in enumerate(check_list, start = 1):
            id_64_bit =  str(user.get_64_bit_id())
            querylist.append(id_64_bit)

            # if our list is list_send_length long or we have reached the end
            if counter % list_send_length == 0 or counter == len(check_list):
                steamids = ",".join(querylist)
                vac = ValveApiCall()
                upp = UpdatePlayerPersonas()
                self.api_context.steamids=steamids
                pass_context = deepcopy(self.api_context)
                chain(vac.s(mode='GetPlayerSummaries',api_context=pass_context), \
                      upp.s()).delay()
                querylist = []
tasks.register(RefreshUpdatePlayerPersonas)


class UpdatePlayerPersonas(ApiFollower):

    def run(self, urldata):
        """Make the avatar and persona facts of a profile match current."""
        #This options is present in the return code, but not needed here.
        #valveOpts = urldata['valveOpts']
        response = urldata['response']

        for pulled_player in response['players']:
            print "Updating " + pulled_player['personaname'] +","+str(pulled_player['steamid'])
            #The PlayerSummaries call returns 64 bit ids.  It is super annoying.
            id_32bit = int(pulled_player['steamid']) % ADDER_32_BIT

            player, created = Player.objects.get_or_create(steam_id=id_32bit)
            player.persona_name = pulled_player['personaname']
            player.profile_url = pulled_player['profileurl']
            player.avatar = pulled_player['avatar']
            player.avatar_medium = pulled_player['avatarmedium']
            player.avatar_full = pulled_player['avatarfull']
            player.save()
tasks.register(UpdatePlayerPersonas)


class RefreshPlayerMatchDetail(BaseTask):

    def run(self):
        """ Go through the users for whom update is True and pull match histories
        since their last scrape time"""
        users = Player.objects.filter(updated=True).select_related()
        tracked = get_tracks(users)
        check_list = meld(users, tracked)
        check_list = [user for user in check_list]
        for counter, user in enumerate(check_list, start = 1):
            context = ApiContext()
            context.account_id=user.steam_id

            if self.api_context.matches_requested is None:
                context.matches_requested = 20
            else:
                context.matches_requested = self.api_context.matches_requested

            if self.api_context.matches_desired is None:
                context.matches_desired = 20
            else:
                context.matches_desired = self.api_context.matches_desired

            context.deepcopy=True
            context.start_scrape_time=now()
            context.last_scrape_time=user.last_scrape_time
            vac = ValveApiCall()
            rpr = RetrievePlayerRecords()
            chain(vac.s(mode='GetMatchHistory',api_context=context),rpr.s()).delay()
tasks.register(RefreshPlayerMatchDetail)


class AcquirePlayerData(BaseTask):

    def run(self):
        if self.api_context.account_id is None:
            logger.error("Needed an account id, had none, failed.")
        player = Player.objects.get_or_create(steam_id=self.api_context.account_id)[0]
        player.updated = True
        player.save()
        if self.api_context.matches_requested is None:
            self.api_context.matches_requested=100
        self.api_context.start_scrape_time=now()
        self.api_context.last_scrape_time=player.last_scrape_time
        self.api_context.deepycopy=True
        if self.api_context.matches_desired is None:
            self.api_context.matches_desired = 500
        for skill in self.api_context.skill_levels:
            self.api_context.skill=skill

            vac = ValveApiCall()
            rpr = RetrievePlayerRecords()
            pass_context = deepcopy(self.api_context)
            chain(vac.s(mode='GetMatchHistory',api_context=pass_context),rpr.s()).delay()
tasks.register(AcquirePlayerData)

class AcquireHeroSkillData(BaseTask):

    def run(self):
        logger.info("Starting")
        if self.api_context.account_id is not None or self.api_context.hero_id is None:
            logger.error("Not allowed to have an account_id for this, and need a Hero.")
        else:

            logger.info("Context Checking")
            if self.api_context.matches_requested is None:
                self.api_context.matches_requested=100
            self.api_context.deepycopy=False
            if self.api_context.matches_desired is None:
                self.api_context.matches_desired = 100
            self.api_context.skill_levels=[1,2,3]
            logger.info("Looping")
            for skill in self.api_context.skill_levels:
                self.api_context.skill=skill

                vac = ValveApiCall()
                rpr = RetrievePlayerRecords()
                pass_context = deepcopy(self.api_context)
                chain(vac.s(mode='GetMatchHistory',api_context=pass_context),rpr.s()).delay()
            logger.info("Done")
tasks.register(AcquireHeroSkillData)

def upload_match_summary(players,parent_match,refresh_records):
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
            account_id=0 #No acct ID means the player is a bot.
            leaver_status=-1
        kwargs = {
            'match': parent_match,
            'player': Player.objects.get_or_create(
                steam_id=account_id)[0],
            'leaver': LeaverStatus.objects.get_or_create(
                steam_id=leaver_status)[0],
            'player_slot': player['player_slot'],
            'hero': Hero.objects.get_or_create(
                steam_id=player['hero_id'])[0],
            'item_0': player['item_0'],
            'item_1': player['item_1'],
            'item_2': player['item_2'],
            'item_3': player['item_3'],
            'item_4': player['item_4'],
            'item_5': player['item_5'],
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
            pms = PlayerMatchSummary.objects.get(player_slot=player['player_slot'],match=parent_match)
            if refresh_records:
                for key, value in kwargs.iteritems():
                    setattr(pms,key,value)
                pms.save()
            playermatchsummary = pms
        except PlayerMatchSummary.DoesNotExist:
            playermatchsummary = PlayerMatchSummary.objects.get_or_create(**kwargs)[0]


        if 'ability_upgrades' in player.keys():
            for skillpick in player['ability_upgrades']:
                kwargs = {
                    'player_match_summary': playermatchsummary,
                    'ability': Ability.objects.get_or_create(steam_id=
                    skillpick['ability'])[0],
                    'time': skillpick['time'],
                    'level': skillpick['level'],
                }
                SkillBuild.objects.get_or_create(**kwargs)
