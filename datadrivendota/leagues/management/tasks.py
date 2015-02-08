import gc
import urllib2
import datetime
from time import mktime
import socket
import ssl
from uuid import uuid4
from celery import Task, chain
from django.core.files import File
from django.utils.text import slugify
from leagues.models import League, LeagueDossier
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


class MirrorLeagues(Task):

    def run(self):
        c = ApiContext()
        c.refresh_records = True
        vac = ValveApiCall()
        ul = CreateLeagues()
        c = chain(vac.s(api_context=c, mode='GetLeagueListing'), ul.s())
        c.delay()


class CreateLeagues(ApiFollower):
    def run(self, urldata):
        for league in self.result['leagues']:
            l, created = League.objects.get_or_create(
                steam_id=league['leagueid']
                )
            try:
                LeagueDossier.objects.get(
                    league=l,
                )
            except LeagueDossier.DoesNotExist:
                LeagueDossier.objects.create(
                    league=l,
                    name=league['name'],
                    description=league['description'],
                    tournament_url=league['tournament_url'],
                    item_def=league['itemdef']
                )


class UpdateLeagueGames(Task):
    """Pulls in all games for all extant leagues"""

    def run(self, min_date=None):

        if min_date is None:
            min_date = int(
                mktime(
                    datetime.datetime.now().timetuple()
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
    """Annexes the url data for league logos from the item schema and updates the leaguedossier objects"""

    def run(self):
        c = ApiContext()
        vac = ValveApiCall()
        ull = UpdateLeagueLogos()
        c = chain(vac.s(api_context=c, mode='GetSchema'), ull.s())
        c.delay()


class UpdateLeagueLogos(ApiFollower):
    """ Takes a given schema result and annexes logo urls."""

    def run(self, urldata):
        leagues = LeagueDossier.objects.all()
        data = self.result['items']
        mapping = {d['defindex']: d['image_url'] for d in data}
        blank_URL = 'http://s3.amazonaws.com/datadrivendota/images/blank-logo.png'

        logger.info('Forming league URLs for {0} leagues'.format(len(leagues)))
        for leaguedossier in leagues:
            logger.info('Doing {0} (ID: {1}'.format(
                leaguedossier.name,
                leaguedossier.league.steam_id
                ))
            filename = slugify(leaguedossier.name)+'.png'
            try:
                url = mapping[leaguedossier.item_def]
                if url != '':
                    imgdata = urllib2.urlopen(url, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())
                    leaguedossier.logo_image.save(
                        filename, File(open(f.name))
                    )
                    os.remove(f.name)
                else:
                    imgdata = urllib2.urlopen(blank_URL, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())

                    leaguedossier.logo_image.save(
                        filename, File(open(f.name))
                        )
                    os.remove(f.name)

            except (urllib2.URLError, ssl.SSLError, socket.timeout):
                self.retry()
            except (KeyError):
                if leaguedossier.logo_image is None:
                    imgdata = urllib2.urlopen(blank_URL, timeout=5)
                    with open('%s.png' % str(uuid4()), 'w+') as f:
                        f.write(imgdata.read())

                    leaguedossier.logo_image.save(
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

