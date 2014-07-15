import urllib2
import json
from urllib import urlencode
from optparse import make_option
import time

from django.core.management.base import BaseCommand

from datadrivendota.settings.base import STEAM_API_KEY
from matches.models import Match, LobbyType, GameMode, LeaverStatus,\
    PlayerMatchSummary, SkillBuild
from players.models import Player
from heroes.models import Ability, Hero


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--id',
            action='store',
            dest='steam_id',
            default='0',
            help='The Steam ID to get the match history for.'
        ),
        make_option(
            '--startingMatch',
            action='store',
            dest='starting_match',
            help='If you want to start at a particular match id'
        )
    )

    def handle(self, *args, **options):
        optionsDict = {'matches_requested': 25,
                       'key': STEAM_API_KEY,
                       'account_id': options['steam_id'],
                       }
        if options['starting_match'] is not None:
            optionsDict = dict(
                optionsDict.items()
                + [('start_at_match_id', options['starting_match'])]
            )

        start_at = None
        keep_going = True
        while keep_going:
            if start_at is not None:
                optionsDict['start_at_match_id'] = start_at
            url = (
                'https://api.steampowered.com'
                '/IDOTA2Match_570/GetMatchHistory/V001/?' +
                urlencode(optionsDict)
            )

            # slow things down for the API call regs
            time.sleep(1)
            data = json.loads(urllib2.urlopen(url).read())['result']
            # print url, data['results_remaining']

            if data['status'] != 1:
                raise Exception("No Data for that call")

            for result in data['matches']:
                self.parse_match_detail(result['match_id'])
            start_at = data['matches'][-1]['match_id']

            if data['results_remaining'] == 0:
                keep_going = False

    def parse_match_detail(self, match_id):
        """
        Performs an API call to retrieve the summary of a match and uploads
        it. Also compiles the downstream hero-build information. Only if the
        match does not exist are the player summaries imported; this will not
        correctly account for players that unanonymize their data. Also, right
        now it makes an API call for every match even if we have stored it.
        More code to the effect of "Look in the hero slot of the player you
        are searching for, see if it is anonymous, update if so" is needed;
        right now this just trawls for overall match data.
        """
        optionsDict = {'key': STEAM_API_KEY,
                       'match_id': match_id}

        url = (
            'https://api.steampowered.com'
            '/IDOTA2Match_570/GetMatchDetails/V001/?' +
            urlencode(optionsDict)
        )
        time.sleep(1)
        try:
            pageaccess = urllib2.urlopen(url)
        except urllib2.HTTPError, err:
            if err.code == 404:
                print (
                    "Page not found! Aborting match scrape for "
                    + str(match_id)
                    + "  "
                    + url
                )
                return 0
            if err.code == 403:
                print (
                    "Your access was denied. Aborting match scrape for "
                    + str(match_id)
                    + "  "
                    + url
                )
                return 0
            if err.code == 401:
                print (
                    "Unauth'd!  Aborting match scrape for "
                    + str(match_id)
                    + "  "
                    + url
                )
                return 0
            if err.code == 500:
                print (
                    "Server Error! Aborting match scrape for "
                    + str(match_id)
                    + "  "
                    + url
                )

        print match_id, url
        data = json.loads(pageaccess.read())['result']

        kwargs = {
            'season': data['season'],
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
            'league_id': data['leagueid'],
            'positive_votes': data['positive_votes'],
            'negative_votes': data['negative_votes'],
            'game_mode': GameMode.objects.get_or_create(
                steam_id=data['game_mode']
            )[0],
        }

        try:
            match = Match.objects.get(steam_id=data['match_id'])
        except Match.DoesNotExist:
            match = Match.objects.create(**kwargs)
            match.save()
            self.parse_player_match_summaries(
                players=data['players'],
                parent_match=match
            )

    def parse_player_match_summaries(self, players, parent_match):
        """
        Populates the endgame summary data that is associated with a match
        and invokes the build parser.
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
        print "Finished a replay"
