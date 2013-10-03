from matches.models import Match, LobbyType, GameMode,\
 LeaverStatus, PlayerMatchSummary, SkillBuild
from datadrivendota.settings.base import STEAM_API_KEY
from players.models import Player
from heroes.models import Ability, Hero
from settings.base import ADDER_32_BIT

from time import time as now
### Patch for <urlopen error [Errno -2] Name or service not known in urllib2
import os
os.environ['http_proxy']=''
### End Patch
import urllib2
import json
from urllib import urlencode
from celery import Task, chain
from celery.registry import tasks
import logging


from httplib import BadStatusLine

logger = logging.getLogger(__name__)

#Parents
class BaseTask(Task):

    abstract=True
    def __call__(self, *args, **kwargs):
        #logger.info("Starting to run")
        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        #logger.info("Ending run")
        pass


class ApiFollower(BaseTask):

    abstract=True
    def __call__(self, *args, **kwargs):
        self.valveOpts = args[0].get('valveOpts',{})
        self.internalOpts = args[0].get('internalOpts',{})
        self.result = args[0].get('result',{})
        #logger.info("I think I assigned things.")
        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        #exit point of the task whatever is the state
        #logger.info("Ending run")
        pass

    def moreResultsLeft(self):
        return self.result['results_remaining'] != 0 \
          and self.internalOpts['last_scrape_time'] < \
            self.result['matches'][-1]['start_time']

#Descendants
class ValveApiCall(BaseTask):

    def run(self, mode, valveOpts={}, internalOpts={}, **kwargs):
        """ Ping the valve API for downloading results.  Only enumeratd modes are
        acceptable; check the code.  There is a natural rate limit here at 1/s
        per valve specifications.  There should be a monthly one too.
        For lots more docs, see http://dev.dota2.com/showthread.php?t=58317 """
        # The steam API accepts a limited set of URLs, and requires a key
        valveOpts['key'] = STEAM_API_KEY
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
            raise KeyError('That mode ('+str(mode)+") is not supported")

        URL = url + '?' + urlencode(valveOpts)
        logger.info("URL: "+ URL)
        # Exception handling for the URL opening.
        try:
            pageaccess = urllib2.urlopen(URL)
        except urllib2.HTTPError, err:
            if err.code == 104:
                logger.info("Got error 104 (connection reset by peer) for mode " + str(mode) + valveOpts + ".  Retrying.")
                self.retry(mode, valveOpts, internalOpts)
            elif err.code == 111:
                logger.info("Connection Refused! "+URL+ ".  Retrying.")
                self.retry(mode, valveOpts, internalOpts)
            elif err.code == 404:
                logger.info("Page not found! "+URL+ ".  Retrying.")
                self.retry(mode, valveOpts, internalOpts)
            elif err.code == 403:
                logger.info("Your access was denied. "+URL+ ".  Retrying.")
                self.retry(mode, valveOpts, internalOpts)
            elif err.code == 401:
                logger.info("Unauth'd! "+URL+ ".  Retrying.")
                self.retry(mode, valveOpts, internalOpts)
            elif err.code == 500:
                print "Server Error! "+URL+ ".  Retrying."
                self.retry(mode, valveOpts, internalOpts)
            elif err.code == 503:
                print "Server busy or limit exceeded "+URL+ ".  Retrying."
                self.retry(mode, valveOpts, internalOpts)
            else:
                print "Got error "+str(err)+" with URL "+URL+ ".  Retrying."
                self.retry(mode, valveOpts, internalOpts)
        except BadStatusLine:
            print "Bad status line for url %s" % URL+ ".  Retrying."
            self.retry(mode, valveOpts, internalOpts)


        # If everything is kosher, import the result and return it.
        data = json.loads(pageaccess.read())
        # Append the options given so we can tell what the invocation was.
        # For example, it is not straightforward to deduce the calling account_id
        # unless you do this.
        data['valveOpts'] = valveOpts
        data['internalOpts'] = internalOpts
        return data
tasks.register(ValveApiCall)


class RetrievePlayerRecords(ApiFollower):

    def run(self, urldata):
        """
        Recursively pings the valve API to get match data and spawns new tasks
        to deal with the downloaded match IDs.
        """
        #Validate
        if self.result['status'] == 15:
            logger.error("Could not pull data. "+str(self.valveOpts['account_id'])+" disallowed it. ")
        elif self.result['status'] == 1:
            #Spawn a bunch of match detail queries
            self.spawnDetailCalls()
            #Go around again if there are more records and the last one was before last scrape.
            if self.moreResultsLeft():
                self.rebound()
            #Successful closeout
            else:
                self.cleanup()
        else:
            logger.error("Unhandled status: "+str(self.result['status']))
            raise Exception("No Data for that call")

    def rebound(self):
        self.valveOpts['start_at_match_id'] = self.result['matches'][-1]['match_id']
        vac = ValveApiCall()
        rpr = RetrievePlayerRecords()
        chain(vac.s('GetMatchHistory',self.valveOpts,self.internalOpts), rpr.s()).delay()

    def cleanup(self):
        player = Player.objects.get(steam_id=self.valveOpts['account_id'])
        new_last_scrape = self.internalOpts['start_scrape_time'] if self.internalOpts['start_scrape_time'] else now()
        player.last_scrape_time = new_last_scrape
        player.save()

    def spawnDetailCalls(self):
        for result in self.result['matches']:
            vac = ValveApiCall()
            um = UploadMatch()
            chain(vac.s('GetMatchDetails',\
                                 {'match_id': result['match_id']},
                                 self.internalOpts), um.s()).delay()
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
        }

        try:
            match = Match.objects.get(steam_id=data['match_id'])
        except Match.DoesNotExist:
            match = Match.objects.create(**kwargs)
            match.save()
            ums = UploadMatchSummary()
            ums.s(players=data['players'], parent_match=match).delay()

tasks.register(UploadMatch)


class UploadMatchSummary(BaseTask):

    def run(self, players, parent_match):
        """
        Populates the endgame summary data that is associated with a match
        and invokes the build parser.  This needs to be fixed for players that
        unanonymize by checking on hero_slot, ignoring player, and updating
        if new data has been included (in particular, which player we are
        talking about).
        """
        for player in players:
            kwargs = {
                'match': parent_match,
                'player': Player.objects.get_or_create(
                    steam_id=player['account_id'])[0],
                'leaver': LeaverStatus.objects.get_or_create(
                    steam_id=player['leaver_status'])[0],
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

tasks.register(UploadMatchSummary)


class RefreshUpdatePlayerPersonas(BaseTask):

    def run(self):
        """ Go through the users for whom update is True and group them into lists
        of 50.  The profile update API actually supports up to 100"""
        list_send_length = 50
        users = Player.objects.filter(updated=True)
        querylist = []

        for counter, user in enumerate(users, start = 1):
            id_64_bit =  str(user.get_64_bit_id())
            querylist.append(id_64_bit)

            # if our list is list_send_length long or we have reached the end
            if counter % list_send_length == 0 or counter == len(users):
                steamids = ",".join(querylist)
                vac = ValveApiCall()
                upp = UpdatePlayerPersonas()
                chain(vac.s('GetPlayerSummaries',\
                                     {'steamids': steamids}), \
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
        users = Player.objects.filter(updated=True)

        for counter, user in enumerate(users, start = 1):
            valveOpts = {'account_id': user.steam_id}
            internalOpts = {'start_scrape_time':now(),
                        'last_scrape_time':user.last_scrape_time}
            vac = ValveApiCall()
            rpr = RetrievePlayerRecords()
            chain(vac.s('GetMatchHistory',valveOpts,internalOpts),
                rpr.s()).delay()

tasks.register(RefreshPlayerMatchDetail)
