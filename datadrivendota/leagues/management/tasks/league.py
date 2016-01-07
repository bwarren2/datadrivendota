""" Tasks to manage leagues. """
import sys
import os
import logging
import requests
from io import BytesIO
from time import mktime
from datetime import datetime, timedelta
from celery import Task, chain

from django.utils.text import slugify
from django.core.files import File
from django.conf import settings
from utils.accessors import get_league_schema
from leagues.models import League, ScheduledMatch
from matches.models import Match
from datadrivendota.management.tasks import (
    ApiFollower,
    ApiContext,
    ValveApiCall,
)
from matches.management.tasks import CycleApiCall

# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
os.environ['http_proxy'] = ''
# End Patch


logger = logging.getLogger(__name__)


class UpdateLeagues(Task):

    """
    Reflect the current item schema data for a league.

    Pings for a logo, gets matches, and hits the item schema.
    """

    def run(self, leagues, matches=10):

        logger.info("Updating the given leagues {0}".format(leagues))
        self.schema = get_league_schema()

        for league_id in leagues:
            try:
                self.create(league_id)
                self.logo_update(league_id)
                self.game_update(league_id, matches)
            except KeyError:
                logger.warning(
                    "Can't update {0}.".format(league_id), exc_info=True
                )

    def create(self, league_id):
        logger.info('Creating {0} as part of leagueupdate'.format(league_id))
        data = self.schema[league_id]

        league = League.objects.get_or_create(steam_id=league_id)[0]
        league.name = data['name']
        league.description = data.get('item_description', None)
        league.tournament_url = data.get('tournament_url', None)
        league.item_def = data['itemdef']

        league.fantasy = self._get_fantasy(data, league_id)
        league.tier = self._get_tier(data, league_id)
        league.save()

    def _get_tier(self, data, league_id):
        usage_def = self._get_def(data)
        if 'tier' in usage_def:
            tier = usage_def['tier']
            if tier == 'professional':
                return League.PRO
            elif tier == 'amateur':
                return League.AMATEUR
            elif tier == 'premium':
                return League.PREMIUM
            else:
                raise Exception(
                    'Tier type {0} for league steam id {1} is ???'.format(
                        tier,
                        league_id
                    )
                )

    def _get_fantasy(self, data, league_id):
        usage_def = self._get_def(data)

        if 'fantasy' in usage_def:
            fantasy = usage_def['fantasy']
            if fantasy == '0':
                return False
            elif fantasy == '1':
                return True
            else:
                raise Exception(
                    'fantasy of {0} for league steam id {1} is ???'.format(
                        fantasy,
                        league_id
                    )
                )
        else:
            return None

    def _get_def(self, data):
        return data.get('tool', {}).get('usage', {})

    def logo_update(self, league_id):
        data = self.schema[league_id]
        vac = ValveApiCall()
        ul = UpdateLeagueLogo()
        c = ApiContext()
        c.league_id = league_id
        iconname = data['image_inventory'].split('/')[-1]
        c.iconname = iconname
        logger.info(
            'Updating logo for {0} as part of leagueupdate'.format(league_id)
        )

        chain(
            vac.s(mode='GetItemIconPath', api_context=c),
            ul.s()
        ).delay()

    def game_update(self, league_id, matches):
        c = ApiContext()
        c.league_id = league_id
        c.tournament_games_only = True
        c.matches_requested = matches
        c.matches_desired = matches
        c.skill = 4
        vac = ValveApiCall()
        rpr = CycleApiCall()
        logger.info(
            'Getting matches {1} for {0} as part of leagueupdate'.format(
                league_id, matches
            )
        )
        ch = chain(
            vac.s(api_context=c, mode='GetMatchHistory'),
            rpr.s()
        )
        ch.delay()


class UpdateLeagueLogo(ApiFollower):

    """ Takes an Item Icon URL ping and saves it to a league logo. """

    def run(self, api_context, json_data, response_code, url):
        league = League.objects.get(steam_id=api_context.league_id)

        json_data = json_data['result']

        # It seems this is the error for a bad ugc id, based on hand test
        if json_data.get('status', {}).get('code', {}) == 9:
            self.fake_league_image(league)
        else:
            url = '{0}{1}'.format(
                settings.VALVE_CDN_PATH,
                json_data['path']
            )
            logging.info('Getting league logo at {0}'.format(url))
            try:
                resp = requests.get(url)
                if resp.status_code == 200:

                    # Saving an image to db from a file buffer.
                    buff = BytesIO(resp.content)
                    buff.seek(0)
                    filename = slugify(league.steam_id) + '_full.png'
                    league.stored_image.save(filename, File(buff))
                league.save()
            except:
                logging.error("No image for {0}!".format(
                    league.steam_id
                    ), exc_info=True
                )

    def fake_league_image(self, league):
        league.image_failed = True
        league.save()


class MirrorRecentLeagues(Task):

    """
    Find the leagues that have recent/upcoming games and re-ping their data.

    Meant to run once a day(ish) via celery beat.
    """

    def run(self):
        leagues = self.find_leagues()
        logger.info("Mirroring these leagues: {0}".format(leagues))
        ul = UpdateLeagues()
        ul.s().delay(leagues=leagues)

    def find_leagues(self):
        """
        Find matches from the last few days that have leagues.

        Get the distinct ids as a list.
        """
        # The .distinct() method fails with sqlite, so in the interests of
        # testing we do this goofy list(set()) business.
        recent_games = set(
            Match.objects.filter(
                start_time__gte=mktime(
                    (
                        datetime.now() - timedelta(
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
