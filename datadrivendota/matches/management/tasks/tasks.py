from datadrivendota.settings.base import STEAM_API_KEY
import urllib2
import json
from urllib import urlencode

from celery import task

#from matches.models import Match, LobbyType, GameMode, LeaverStatus,\
#    PlayerMatchSummary, SkillBuild
#from steamusers.models import SteamUser
#from heroes.models import Ability, Hero


@task(rate_limit='1/s')
def valve_api_call(mode, optionsDict={}):
    """Ping the valve API for downloading results.  Only enumeratd modes are
    acceptable; check the code.  There is a natural rate limit here at 1/s
    per valve specifications.  There should be a monthly one too.:"""

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

    try:
        url = modeDict[mode]
    except KeyError:
        raise KeyError('That mode ('+str(mode)+") is not supported")

    URL = url + '?' + urlencode(optionsDict)
    data = json.loads(urllib2.urlopen(URL).read())['result']
    return data


def retreive_player_records(account_id, matches_requested=25):
    optionsDict = {'matches_requested': matches_requested,
                   'key': STEAM_API_KEY,
                   'account_id': account_id,
                   }
    if options['starting_match'] is not None:
        optionsDict = dict(optionsDict.items() + [('start_at_match_id', options['starting_match'])])

    start_at = None
    keep_going = True
    while keep_going:

        if start_at is not None:
            optionsDict['start_at_match_id'] = start_at

        URL = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?' + \
            urlencode(optionsDict)

        data = json.loads(urllib2.urlopen(URL).read())['result']
        print URL, data['results_remaining']

        if data['status'] != 1:
            raise Exception("No Data for that call")

        for result in data['matches']:
            parse_match_detail(result['match_id'])
        start_at = data['matches'][-1]['match_id']

        if data['results_remaining'] == 0:
            keep_going = False
    return False
