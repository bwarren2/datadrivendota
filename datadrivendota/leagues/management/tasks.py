import os
import logging
import json
import requests
from collections import defaultdict
from io import BytesIO
from time import mktime
from datetime import datetime, timedelta
from celery import Task, chain

from django.conf import settings

from datadrivendota.redis_app import redis_app as redis
from datadrivendota.redis_app import timeline_key, slice_key, set_games
from utils.accessors import get_league_schema
from leagues.models import League
from heroes.models import Hero
from items.models import Item
from teams.models import Team
from leagues.models import ScheduledMatch
from matches.models import Match
from datadrivendota.management.tasks import (
    ApiFollower,
    ApiContext,
    ValveApiCall,
)
from matches.management.tasks import MirrorMatches, CycleApiCall

# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
os.environ['http_proxy'] = ''
# End Patch


logger = logging.getLogger(__name__)


class MirrorLiveGames(Task):
    """
    Pings live game JSON and passes it to redis updater
    """

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
    """
    Sets the redis store of live json to the retrieved result
    """
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
                formatted_game[side] = self._get_side_data(game, side)

            self._store_data(formatted_game)

        set_games(urldata)

    def _store_data(self, game_snapshot):
        # Store slice
        expiry_seconds = 60*60*24*100  # 1 day
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
            extant['radiant'] = game_snapshot['radiant']
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
        game_dict['league_logo_url'] = game['league_id']
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
                        + player['assists']/2.0
                    players.append(player)
            else:
                pass  # Nothing to see here

        return players

    def _get_heroes(self):
        self.hero_urls = {
            x.steam_id: x.mugshot.url for x in Hero.objects.all()
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
        update_teams = []
        update_leagues = []
        for game in data:

            # Do Teams
            for team_type in ['radiant_team', 'dire_team']:
                if team_type in game.keys():
                    if 'team_id' in game[team_type].keys():
                        team_id = game[team_type]['team_id']
                        team, t_created = Team.objects.get_or_create(
                            steam_id=team_id
                            )
                        game[team_type]['logo_url'] = team.image

            # Do League
            league_id = game['league_id']
            league, l_created = League.objects.get_or_create(
                steam_id=league_id
                )
            game['league_logo_url'] = league.image

        self.update_leagues = update_leagues
        self.update_teams = update_teams

        return data

    def _setup(self, urldata):
        urldata = self._clean_urldata(urldata)
        self._get_heroes()
        self._get_items()
        return urldata

    def _clean_urldata(self, urldata):
        """
        Strips out request-level response from valve.
        """
        return urldata['result']['games']


class MirrorLeagueSchedule(Task):
    """
    Kicks off the API call to match schedules with Valve,
    and passes the result to Update
    """
    def run(self):

        logger.info("Reflecting Valve's view of upcoming matches with local")
        context = ApiContext()
        vac = ValveApiCall()
        uls = UpdateLeagueSchedule()
        c = chain(
            vac.s(api_context=context, mode='GetScheduledLeagueGames'),
            uls.s()
        )
        c.delay()


class UpdateLeagueSchedule(ApiFollower):
    """
    Take the scheduled league games and reflect them in our scheduled matches.
    """

    def run(self, urldata):

        logger.info("Saving the schedule")
        data = self.clean_urldata(urldata)
        self.delete_unscheduled_games(data)
        self.create_scheduled_games(data)

    def delete_unscheduled_games(self, data):
        """
        Iterate through scheduled matches and purge games not on the schedule.

        One-by-one is slow, but there should never be many of these.
        """
        logger.info('Deleting unscheduled games')
        impending_matches = []
        for x in data['games']:
            if len(x['teams']) == 2:
                datum = (
                    x['league_id'],
                    x['game_id'],
                    x['teams'][0]['team_id'],
                    x['teams'][1]['team_id'],
                )
            elif len(x['teams']) == 1:
                datum = (
                    x['league_id'],
                    x['game_id'],
                    x['teams'][0]['team_id'],
                    None,
                )
            elif len(x['teams']) == 0:
                datum = (
                    x['league_id'],
                    x['game_id'],
                    None,
                    None,
                )
            else:
                raise Exception(
                    "I don't know what this team set is: {0}".format(x)
                )
            impending_matches.append(datum)

        matches = ScheduledMatch.objects.all()
        for match in matches:
            imprint = self._fingerprint(match)
            if imprint not in impending_matches:
                logger.info('Deleting {0}'.format(imprint))
                match.delete()

    def create_scheduled_games(self, data):
        """
        Make new games based on the schedule.

        Keying on the attributes of the match is goofy, but effective.
        @todo: make this a bulk_insert for speediness if needed.
        """
        logger.info('Creating scheduled games')
        for game in data['games']:
            league = League.objects.get_or_create(
                steam_id=game['league_id']
            )[0]
            if len(game['teams']) > 0:
                team_1 = Team.objects.get_or_create(
                    steam_id=game['teams'][0]['team_id']
                )[0]
            else:
                team_1 = None

            if len(game['teams']) > 1:
                team_2 = Team.objects.get_or_create(
                    steam_id=game['teams'][1]['team_id']
                )[0]
            else:
                team_2 = None

            try:
                ScheduledMatch.objects.get(
                    league__steam_id=league.steam_id,
                    team_1=team_1,
                    team_2=team_2,
                    game_id=game['game_id'],
                    start_time=game['starttime'],
                    )
            except ScheduledMatch.DoesNotExist:
                ScheduledMatch.objects.create(
                    league=league,
                    team_1=team_1,
                    team_2=team_2,
                    game_id=game['game_id'],
                    start_time=game['starttime'],
                    comment=game['comment'],
                    final=game['final'],
                )

    def clean_urldata(self, urldata):
        """
        Strips out request-level response from valve.
        """
        return urldata['result']

    def _fingerprint(self, scheduled_match):
        """
        Utility function for effective-PKness of an object.

        @todo: use unique-together and improve style to do the same thing.
        """
        l_id = scheduled_match.league_id
        g_id = scheduled_match.game_id
        if scheduled_match.team_1:
            t_1 = scheduled_match.team_1.steam_id
        else:
            t_1 = None

        if scheduled_match.team_2:
            t_2 = scheduled_match.team_2.steam_id
        else:
            t_2 = None

        return (
            l_id,
            g_id,
            t_1,
            t_2,
        )


class UpdateLeagues(Task):
    """
    Reflects the current item schema data for a league and pings for a logo
    """
    def run(self, leagues, matches=10):
        """
        Presumes iterable of steam ids, hits redis cache of item schema,
        pings valve per league for the item image
        """
        logger.info("Updating the given leagues {0}".format(leagues))
        schema = get_league_schema()

        for league_id in leagues:
            try:
                data = schema[league_id]
                league = League.objects.get_or_create(steam_id=league_id)[0]
                league.name = data['name']
                league.description = data['item_description']
                league.tournament_url = data['tournament_url']
                league.item_def = data['itemdef']
                league.save()

                # Get a new logo
                vac = ValveApiCall()
                ul = UpdateLeagueLogo()
                c = ApiContext()
                c.league_id = league_id
                iconname = data['image_inventory'].split('/')[-1]
                c.iconname = iconname
                chain(
                    vac.s(mode='GetItemIconPath', api_context=c),
                    ul.s()
                ).delay()

                # Retrieve recent games
                c = ApiContext()
                c.league_id = league.steam_id
                c.tournament_games_only = True
                c.matches_requested = matches
                c.matches_desired = matches
                c.skill = 4
                vac = ValveApiCall()
                rpr = CycleApiCall()
                ch = chain(
                    vac.s(api_context=c, mode='GetMatchHistory'),
                    rpr.s()
                )
                ch.delay()
            except KeyError:
                logger.error("Can't find {0} in schema.  :(".format(league_id))


class UpdateLeagueLogo(ApiFollower):
    """
    Takes an Item Icon URL ping and saves it to a league logo
    """
    def run(self, urldata):
        league = League.objects.get(steam_id=self.api_context.league_id)
        url = '{0}{1}'.format(
            settings.VALVE_CDN_PATH,
            urldata['result']['path']
        )

        resp = requests.get(url)
        if resp.status_code == 200:
            buff = BytesIO(resp.content)
            _ = buff.seek(0)  # Stop random printing.
            #  If we wanted to, we would store the league logo data here.
            #  We are currently working out whether to hotlink to Valve.

        league.valve_cdn_image = url
        league.save()


class MirrorLeagues(Task):
    """
    Get the big list of leagues and reflect it
    """
    def run(self):
        logger.info("Reflecting Valve's view of upcoming matches with local")
        context = ApiContext()
        vac = ValveApiCall()
        cl = CreateLeagues()
        c = chain(
            vac.s(api_context=context, mode='GetLeagueListing'),
            cl.s()
        )
        c.delay()


class CreateLeagues(ApiFollower):
    """
    Takes all the results from a league list call and inserts them.
    """
    def run(self, urldata):
        league_list = []
        for league in self.result['leagues']:
            League.objects.update_or_create(
                steam_id=league['leagueid'],
                defaults={
                    'name': league['name'],
                    'description': league['description'],
                    'tournament_url': league['tournament_url'],
                    'item_def': league['itemdef'],
                }
            )
            league_list.append(league['leagueid'])
        UpdateLeagues().s().delay(leagues=league_list, matches=1)


class MirrorRecentLeagues(Task):
    """
    Find the leagues that have recent/upcoming games and re-ping their data.

    Meant to run once a day(ish) via celery beat
    """
    def run(self):
        leagues = self.find_leagues()
        ul = UpdateLeagues()
        ul.s().delay(leagues=leagues)

    def find_leagues(self):
        """
        Find matches from the last few days that have leagues,
        and get the distinct ids as a list
        """

        # The .distinct() method fails with sqlite, so in the interests of
        # testing we do this goofy list(set()) business.
        recent_games = set(
            Match.objects.filter(
                start_time__gte=mktime(
                    (
                        datetime.now()-timedelta(
                            days=settings.LOOKBACK_UPDATE_DAYS
                            )
                    ).timetuple()
                )
            )
            .exclude(league=None)
            .values_list('league__steam_id', flat=True)
        )

        recent_schedule = set(
            ScheduledMatch.objects.all()
            .values_list('league__steam_id', flat=True)
        )
        recent_games.update(recent_schedule)
        if recent_games is None:
            return []
        else:
            return recent_games


class AcquireHiddenLeagueGames(Task):
    """Deprecated.  A stupid hack to get 'secret' TI4 games."""

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
    """Deprecated.  A stupid hack to get 'secret' TI4 games."""

    def run(self, urldata):
        matches = [match['match_id'] for match in urldata['result']['matches']]
        am = MirrorMatches()
        am.delay(matches=matches, skill=4)
