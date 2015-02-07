import json
from StringIO import StringIO
import gc
import urllib2
from datetime import timedelta
from django.utils import timezone
from time import mktime
import socket
import ssl
from uuid import uuid4
from celery import Task, chain
from django.conf import settings
from datadrivendota.redis_app import redis_app as redis
from django.core.files import File
from django.utils.text import slugify
from leagues.models import League
from utils.accessors import get_league_schema
from teams.models import Team
from teams.management.tasks import MirrorTeamDetails
from leagues.models import ScheduledMatch
import logging
from datadrivendota.management.tasks import (
    ApiFollower,
    ApiContext,
    ValveApiCall,
)
from matches.management.tasks import MirrorMatches, CycleApiCall

# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
import os
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
            vac.s(api_context=c, mode='GetSchemaURL'),
            ulg.s()
        )
        c.delay()


class UpdateLiveGames(ApiFollower):
    """
    Sets the redis store of live json to the retrieved result
    """
    def run(self, urldata):

        urldata = self._clean_urldata(urldata)

        teams = self._find_update_teams(urldata)
        self._update_teams(teams)
        leagues = self._find_update_leagues(urldata)
        self._update_leagues(leagues)

        data = self._merge_logos(urldata)
        self._store_data(data)

    def _merge_logos(self, data):
        for game in data['games']:

            # Do Teams
            for team_type in ['radiant_team', 'dire_team']:
                if team_type in game.keys():
                    if 'team_id' in game[team_type].keys():
                        try:
                            team_id = game[team_type]['team_id']
                            team = Team.objects.get(
                                steam_id=team_id
                                )
                            if team.logo_image:
                                logo_url = team.logo_image.url
                                game[team_type]['logo_url'] = logo_url
                            else:
                                game[team_type]['logo_url'] = ''
                        except Team.DoesNotExist:
                            game[team_type]['logo_url'] = ''
            # Do League
            try:
                league_id = game['league_id']
                league = League.objects.get(
                    steam_id=league_id
                    )
                if league.logo_image:
                    logo_url = league.logo_image.url
                    game['league_logo_url'] = logo_url
                else:
                    game['league_logo_url'] = ''
            except League.DoesNotExist:
                game['league_logo_url'] = ''

        return data

    def _store_data(self, data):
        # redis.set(settings.LIVE_JSON_KEY, json.dumps(urldata['result']))
        redis.set(settings.LIVE_JSON_KEY, json.dumps(data))

    def _find_update_teams(self, data):
        update_teams = []
        for game in data['games']:
            # Do Teams
            for team_type in ['radiant_team', 'dire_team']:
                if team_type in game.keys():
                    if 'team_id' in game[team_type].keys():
                        try:
                            team_id = game[team_type]['team_id']
                            Team.objects.get(
                                steam_id=team_id
                            )
                        except Team.DoesNotExist:
                            update_teams.append(team_id)
        return update_teams

    def _find_update_leagues(self, data):
        update_leagues = []
        for game in data['games']:
            try:
                league_id = game['league_id']
                League.objects.get(
                    steam_id=league_id
                )
            except League.DoesNotExist:
                game['league_logo_url'] = ''
                update_leagues.append(league_id)
        return update_leagues

    def _update_teams(self, update_teams):
        if update_teams is not None:
            logger.info('Updating these teams: {0}'.format(update_teams))
            mtd = MirrorTeamDetails()
            mtd.s(teams=update_teams).delay()

    def _update_leagues(self, update_leagues):
        if update_leagues is not None:
            logger.info('Updating these leagues: {0}'.format(update_leagues))
            ul = UpdateLeagues()
            ul.s(leagues=update_leagues).delay()

    def _clean_urldata(self, urldata):
        """
        Strips out request-level response from valve.
        """
        return urldata['result']


class MirrorLeagueSchedule(Task):
    """
    Kicks off the API call to match schedules with Valve, and passes the result to Update
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
        teams = self.find_update_teams(data)
        self.update_teams(teams)
        leagues = self.find_update_leagues(data)
        self.update_leagues(leagues)

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

    def find_update_teams(self, data):
        """
        Check each team for missing logo/outdated timestamp.

        Results get passed to update task
        """
        update_teams = set()
        for game in data['games']:
            # Use get because we just made these
            for team_info in game['teams']:

                team = Team.objects.get(
                    steam_id=team_info['team_id']
                )

                if self._object_outdated(team):
                    update_teams.add(team.steam_id)

        logger.info("Teams that need updating: {0}".format(update_teams))
        return update_teams

    def find_update_leagues(self, data):
        """
        Check each league for missing logo/outdated timestamp.

        Results get passed to update task
        """
        update_leagues = set()
        for game in data['games']:
            # Use get because we just made these
            league = League.objects.get(
                steam_id=game['league_id']
            )
            print self._object_outdated(league), league
            if self._object_outdated(league):
                update_leagues.add(league.steam_id)
        logger.info("Leagues that need updating: {0}".format(update_leagues))
        return update_leagues

    def update_teams(self, teams):
        """
        Kicks off the celery task to fix teams that need work.
        """
        mtd = MirrorTeamDetails()
        mtd.s(teams=teams).delay()

    def update_leagues(self, leagues):
        """
        Kicks off the celery task to fix teams that need work.
        """
        ul = UpdateLeagues()
        ul.s(leagues=leagues).delay()

    def _object_outdated(self, obj):
        """
        Works for either team or league.
        """
        if (
            obj.logo_image.name is None
            or obj.logo_image.name == None
            or obj.logo_image.name == ''
            or obj.update_time < (
                timezone.now() - timedelta(
                    seconds=settings.UPDATE_LAG_UTC
                )
            )
        ):
            return True
        else:
            return False

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


class MirrorLeagues(Task):
    """
    DEPRECATED

    Tries to make ALL THE LEAGUES off the list.
    """

    def run(self):
        c = ApiContext()
        c.refresh_records = True
        vac = ValveApiCall()
        ul = CreateLeagues()
        c = chain(vac.s(api_context=c, mode='GetLeagueListing'), ul.s())
        c.delay()


class CreateLeagues(ApiFollower):
    """
    DEPRECATED

    Takes all the results from a league list call and inserts them.
    """
    def run(self, urldata):
        for league in self.result['leagues']:
            l, created = League.objects.get_or_create(
                steam_id=league['leagueid']
                )
            l.update(
                name=league['name'],
                description=league['description'],
                tournament_url=league['tournament_url'],
                item_def=league['itemdef'],
            )


class UpdateLeagues(Task):
    """
    Reflects the current item schema data for a league and pings for a logo
    """
    def run(self, leagues):
        """
        Presumes iterable of steam ids, hits redis cache of item schema, pings valve per league for the item image
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
                c.matches_requested = 25
                c.matches_desired = 100
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
        filename = '{0}.png'.format(self.api_context.iconname)
        url = '{0}{1}'.format(
            settings.VALVE_CDN_PATH,
            urldata['result']['path']
        )

        imgdata = urllib2.urlopen(url, timeout=5)

        with open('%s.png' % str(uuid4()), 'w+') as f:
            f.write(imgdata.read())

        league.logo_image.save(
            filename, File(open(f.name))
            )
        league.valve_cdn_image = url
        league.save()
        os.remove(f.name)


class UpdateLeagueGames(Task):
    """
    DEPRECATED

    Pulls in all games for all extant leagues
    """

    def run(self, min_date=None):

        if min_date is None:
            min_date = int(
                mktime(
                    timezone.now().timetuple()
                ) - 7*24*60*60
            )

        if min_date != 'all':
            c = ApiContext()
            c.matches_requested = 500
            c.matches_desired = 500
            c.date_min = min_date
            c.skill = 4
            vac = ValveApiCall()
            alg = MirrorLeagueGames()
            c = chain(
                vac.s(api_context=c, mode='GetScheduledLeagueGames'),
                alg.s()
            )
            c.delay()

        elif min_date == 'all':
            for league in League.objects.all():
                c = ApiContext()
                c.league_id = league.steam_id
                c.matches_requested = 500
                c.matches_desired = 500
                c.skill = 4
                vac = ValveApiCall()
                rpr = CycleApiCall()
                ch = chain(
                    vac.s(api_context=c, mode='GetMatchHistory'),
                    rpr.s()
                )
                ch.delay()
        else:
            raise Exception("What is this min_date?: {0}".format(min_date))


class MirrorLeagueGames(ApiFollower):
    """
    DEPRECATED
    """
    def run(self, urldata):
        data = self.result['games']
        leagues = [game['league_id'] for game in data]
        for league_id in leagues:
            c = ApiContext()
            c.league_id = league_id
            c.date_min = self.api_context.date_min
            c.matches_requested = 500
            c.matches_desired = 500
            c.skill = 4
            vac = ValveApiCall()
            rpr = CycleApiCall()
            c = chain(
                vac.s(api_context=c, mode='GetMatchHistory'),
                rpr.s()
            )
            c.delay()


class MirrorLeagueLogos(Task):
    """
    DEPRECATED

    Annexes the url data for league logos from the item schema and updates the logo fields
    """

    def run(self):
        c = ApiContext()
        vac = ValveApiCall()
        ull = UpdateLeagueLogos()
        c = chain(vac.s(api_context=c, mode='GetSchema'), ull.s())
        c.delay()


class UpdateLeagueLogos(ApiFollower):
    """ Takes a given schema result and annexes logo urls."""

    def run(self, urldata):
        raise Exception('Geborked filter, fix.')
        leagues = League.objects.filter('')
        data = self.result['items']
        mapping = {d['defindex']: d['image_url'] for d in data}
        blank_URL = (
            'http://s3.amazonaws.com/datadrivendota'
            '/images/blank-logo.png'
        )

        logger.info('Forming league URLs for {0} leagues'.format(len(leagues)))
        for league in leagues:
            logger.info('Doing {0} (ID: {1}'.format(
                league.name,
                league.league.steam_id
                ))
            filename = slugify(league.name)+'.png'
            try:
                url = mapping[league.item_def]
                if url != '':
                    imgdata = urllib2.urlopen(url, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())
                    league.logo_image.save(
                        filename, File(open(f.name))
                    )
                    os.remove(f.name)
                else:
                    imgdata = urllib2.urlopen(blank_URL, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())

                    league.logo_image.save(
                        filename, File(open(f.name))
                        )
                    os.remove(f.name)

            except (urllib2.URLError, ssl.SSLError, socket.timeout):
                self.retry()
            except (KeyError):
                if league.logo_image is None:
                    imgdata = urllib2.urlopen(blank_URL, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())

                    league.logo_image.save(
                        filename, File(open(f.name))
                        )
                    os.remove(f.name)
            imgdata = None
            gc.collect()


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


