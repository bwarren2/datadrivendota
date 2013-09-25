from matches.models import Match, LobbyType, GameMode,\
 LeaverStatus, PlayerMatchSummary, SkillBuild
from datadrivendota.settings.base import STEAM_API_KEY
from players.models import Player
from heroes.models import Ability, Hero
from settings.base import VALVE_RATE, ADDER_32_BIT

import urllib2
import json
from urllib import urlencode
from celery import task, chain

from httplib import BadStatusLine
#from heroes.models import Ability, Hero


@task(rate_limit=VALVE_RATE)
def valve_api_call(mode, optionsDict={}):
    """ Ping the valve API for downloading results.  Only enumeratd modes are
    acceptable; check the code.  There is a natural rate limit here at 1/s
    per valve specifications.  There should be a monthly one too.
    For lots more docs, see http://dev.dota2.com/showthread.php?t=58317 """

    # The steam API accepts a limited set of URLs, and requires a key
    optionsDict['key'] = STEAM_API_KEY
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

    URL = url + '?' + urlencode(optionsDict)
    print "URL: "+ URL
    # Exception handling for the URL opening.
    try:
        pageaccess = urllib2.urlopen(URL)
    except urllib2.HTTPError, err:
        if err.code == 404:
            error = "Page not found! "+URL
            exceptionPrint(error)
        elif err.code == 403:
            error = "Your access was denied. "+URL
            exceptionPrint(error)
        elif err.code == 401:
            error =  "Unauth'd! "+URL
            exceptionPrint(error)
        elif err.code == 500:
            error = "Server Error! "+URL
            exceptionPrint(error)
        elif err.code == 503:
            error = "Server busy or limit exceeded "+URL
            exceptionPrint(error)
        else:
            error = "Got error "+str(err)+" with URL "+URL
            exceptionPrint(error)
    except BadStatusLine:
        error = "Bad status line for url %s" % URL
        exceptionPrint(error)

    # If everything is kosher, import the result and return it.
    data = json.loads(pageaccess.read())
    # Append the options given so we can tell what the invocation was.
    # For example, it is not straightforward to deduce the calling account_id
    # unless you do this.
    data['optionsGiven'] = optionsDict
    return data

@task()
def retrieve_player_records(urldata):
        """
        Recursively pings the valve API and spawns new tasks to deal with the
        downloaded match IDs.
        """
        optionsGiven = urldata['optionsGiven']
        urldata = urldata['result']

        #The API call needs to know what options to use, in this case acct id.
        optionsDict = {'account_id': optionsGiven['account_id']}

        #This function is recursive, and starts at the beginning unless it knows
        #to start in the middle.
        optionsDict['start_at_match_id'] = urldata['matches'][-1]['match_id']

        for result in urldata['matches']:
            chain(valve_api_call.s('GetMatchDetails',\
                                 {'match_id': result['match_id']}), \
                  upload_match.s()).delay()

        if urldata['results_remaining'] != 0:
            chain(valve_api_call.s('GetMatchHistory',optionsDict), \
                  retrieve_player_records.s()).delay()

        if urldata['status'] != 1:
            raise Exception("No Data for that call")

@task()
def upload_match(data):
    """
    Uploads a match given the return of an API call.
    Only if the match does not exist are the player summaries imported;
    this will not correctly account for players that unanonymize their data.
    More code to the effect of "Look in the hero slot of the player you are
    searching for, see if it is anonymous, update if so" is needed;
    right now this just trawls for overall match data.
    """
    data = data['result']
    #optionsGiven = urldata['optionsGiven']

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
        upload_match_summary.s(players=data['players'],
                               parent_match=match).delay()

@task()
def upload_match_summary(players, parent_match):
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

@task()
def refresh_updating_players():
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
            chain(valve_api_call.s('GetPlayerSummaries',\
                                 {'steamids': steamids}), \
                  update_players.s()).delay()
            querylist = []

@task()
def update_players(urldata):
    """Make the avatar and persona facts of a profile match current."""
    #This options is present in the return code, but not needed here.
    #optionsGiven = urldata['optionsGiven']
    response = urldata['response']

    for pulled_player in response['players']:
        #The PlayerSummaries call returns 64 bit ids.  It is super annoying.
        id_32bit = int(pulled_player['steamid']) - ADDER_32_BIT

        player, created = Player.objects.get_or_create(steam_id=id_32bit)
        player.persona_name = pulled_player['personaname']
        player.profile_url = pulled_player['profileurl']
        player.avatar = pulled_player['avatar']
        player.avatar_medium = pulled_player['avatarmedium']
        player.avatar_full = pulled_player['avatarfull']
        player.save()

def exceptionPrint(str):
    print str
    raise RuntimeError(str)
