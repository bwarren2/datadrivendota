""" Tasks to manage leagues. """
import os
import logging
import requests
from io import BytesIO
from time import mktime
from datetime import datetime, timedelta
from celery import Task, chain

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

    """ Takes an Item Icon URL ping and saves it to a league logo. """

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
            _ = _  # Stop the linting.
            #  If we wanted to, we would store the league logo data here.
            #  We are currently working out whether to hotlink to Valve.

        league.valve_cdn_image = url
        league.save()


class MirrorLeagues(Task):

    """ Get the big list of leagues and reflect it. """

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

    """ Takes all the results from a league list call and inserts them. """

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

    Meant to run once a day(ish) via celery beat.
    """

    def run(self):
        leagues = self.find_leagues()
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

        updatable = League.objects.exclude(image_ugc=None).filter(
            valve_cdn_image=None
        )
        recent_games.update(set([t.steam_id for t in updatable]))

        if recent_games is None:
            return []
        else:
            return recent_games
