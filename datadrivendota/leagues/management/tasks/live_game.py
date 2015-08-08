""" Tasks to manage leagues. """
import os
import logging
import json
from collections import defaultdict
from celery import Task, chain

from datadrivendota.redis_app import redis_app as redis
from datadrivendota.redis_app import (
    timeline_key,
    slice_key,
    set_games,
)
from leagues.models import League
from heroes.models import Hero
from items.models import Item
from teams.models import Team
from datadrivendota.management.tasks import (
    ApiFollower,
    ApiContext,
    ValveApiCall,
)

# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
os.environ['http_proxy'] = ''
# End Patch


logger = logging.getLogger(__name__)


class MirrorLiveGames(Task):

    """ Pings live game JSON and passes it to redis updater. """

    def run(self):
        logger.info("Pinging the live league json")
        c = ApiContext()
        vac = ValveApiCall()
        ulg = UpdateLiveGames()
        c = chain(
            vac.s(api_context=c, mode='GetLiveLeagueGames'),
            ulg.s()
        )
        c.delay()


class UpdateLiveGames(ApiFollower):

    """ Sets the redis store of live json to the retrieved result. """

    def run(self, urldata):
        urldata = self._setup(urldata)

        # Do this all at once to group leagues and teams in one pass
        urldata = self._merge_logos(urldata)

        for game in urldata:
            formatted_game = {}
            formatted_game['players'] = self._get_players(game)
            formatted_game['states'] = self._get_states(game)
            formatted_game['pickbans'] = self._get_pickbans(game)
            formatted_game['game'] = self._get_game_data(game)

            for side in ['radiant', 'dire']:
                if self._get_side_data(game, side) is not None:
                    formatted_game[side] = self._get_side_data(game, side)

            self._store_data(formatted_game)

        set_games(urldata)

    def _store_data(self, game_snapshot):
        # Store slice
        expiry_seconds = 60 * 60 * 24 * 100  # 1 day
        key = slice_key(game_snapshot['game']['match_id'])
        redis.set(key, json.dumps(game_snapshot))
        redis.expire(key, expiry_seconds)

        # Merge timeline
        key = timeline_key(game_snapshot['game']['match_id'])
        extant = redis.get(key)
        if extant is not None:
            extant = json.loads(extant)

        timeline = self._merge_slice(game_snapshot, extant)
        extant = redis.set(key, json.dumps(timeline))
        redis.expire(key, expiry_seconds)

    def _merge_slice(self, game_snapshot, extant):
        new_timeslice = {
            'players': game_snapshot['players'],
            'states': game_snapshot['states'],
        }

        if extant is None:
            extant = {}
            # Don't have an existing concat'd json, make one to start
            extant['timeline'] = []
            extant['timeline'].append(new_timeslice)
            extant['game'] = game_snapshot['game']

            if 'radiant' in game_snapshot:
                extant['radiant'] = game_snapshot['radiant']

            if 'dire' in game_snapshot:
                extant['dire'] = game_snapshot['dire']

            extant['pickbans'] = game_snapshot['pickbans']
            return extant
        else:
            times = [x['states']['duration'] for x in extant['timeline']]
            if new_timeslice['states']['duration'] not in times:
                extant['timeline'].append(new_timeslice)
                extant['timeline'].sort(
                    key=lambda item: item['states']['duration']
                )
                return extant
            else:
                return extant

    def _get_side_data(self, game, side):
        if '{0}_team'.format(side) in game.keys():
            datadict = game['{0}_team'.format(side)]
            datadict['wins'] = game['{0}_series_wins'.format(side)]
        else:
            datadict = None

        return datadict

    def _get_game_data(self, game):
        game_dict = {}
        game_dict['league_id'] = game['league_id']
        # game_dict['league_logo_url'] = game['league_id']
        game_dict['league_tier'] = game['league_tier']
        game_dict['lobby_id'] = game['lobby_id']
        game_dict['match_id'] = game['match_id']
        game_dict['series_type'] = game['series_type']
        game_dict['spectators'] = game['spectators']
        game_dict['stream_delay_s'] = game['stream_delay_s']
        #  Fix this:  u'league_tier': 1,

        return game_dict

    def _get_states(self, game):
        state_dict = defaultdict(dict)
        if 'scoreboard' in game:
            state_dict['roshan_timer'] = \
                game['scoreboard']['roshan_respawn_timer']
            state_dict['duration'] = \
                game['scoreboard']['duration']
            for side in ['radiant', 'dire']:
                state_dict['{0}_barracks'.format(side)] =\
                    game['scoreboard'][side]['barracks_state']
                state_dict['{0}_towers'.format(side)] =\
                    game['scoreboard'][side]['tower_state']
        else:
            state_dict['roshan_timer'] = None
            state_dict['duration'] = 0

        state_dict.default_factory = None  # Django can't iterate on ddicts
        return state_dict

    def _get_players(self, game):
        players = []
        if 'scoreboard' in game.keys():
            for side in ['radiant', 'dire']:
                player_list = game['scoreboard'][side]['players']
                for player in player_list:

                    # Incorporate hero data
                    player['hero_url'] = self.hero_urls[player['hero_id']]

                    account_id = player['account_id']
                    player_data = [
                        x for x in game['players']
                        if x['account_id'] == account_id
                    ][0]
                    player['name'] = player_data['name']
                    if player_data['team'] == 0:
                        player['side'] = 'radiant'
                    else:
                        player['side'] = 'dire'

                    player['kda2'] = player['kills'] - player['death']\
                        + player['assists'] / 2.0
                    players.append(player)
            else:
                pass  # Nothing to see here

        return players

    def _get_heroes(self):
        self.hero_urls = {
            x.steam_id: x.mugshot_url for x in Hero.objects.all()
        }

    def _get_items(self):
        self.item_names = {
            x.steam_id: x.internal_name for x in Item.objects.all()
        }

    def _get_pickbans(self, game):
        pickbans = defaultdict(dict)
        for side in ['radiant', 'dire']:
            for choice in ['picks', 'bans']:
                if 'scoreboard' in game:
                    if choice in game['scoreboard'][side]:  # Sometimes rd
                        pickbans[side][choice] = \
                            game['scoreboard'][side][choice]

                        for hero in pickbans[side][choice]:
                            hero['url'] = self.hero_urls[hero['hero_id']]
                    else:
                        pickbans[side][choice] = None
                else:
                    pickbans[side][choice] = None

        return pickbans

    def _merge_logos(self, data):
        for game in data:
            # Do Teams
            for team_type in ['radiant_team', 'dire_team']:
                if team_type in game.keys():
                    if 'team_id' in game[team_type].keys():
                        team_id = game[team_type]['team_id']
                        team, t_created = Team.objects.get_or_create(
                            steam_id=team_id
                        )
                        if team.image_ugc is None:
                            team.image_ugc = game[team_type]['team_logo']
                            team.save()
                        game[team_type]['logo_url'] = team.image

            # Do League
            league_id = game['league_id']
            league, l_created = League.objects.get_or_create(
                steam_id=league_id
            )
            game['league_logo_url'] = league.image

        return data

    def _setup(self, urldata):
        urldata = self._clean_urldata(urldata)
        self._get_heroes()
        self._get_items()
        return urldata

    def _clean_urldata(self, urldata):
        """ Strip out request-level response from valve. """
        return urldata['result']['games']
