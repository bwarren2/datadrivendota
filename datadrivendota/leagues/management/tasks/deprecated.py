""" Tasks to manage leagues. """
import os
import logging
from celery import Task, chain

from datadrivendota.management.tasks import (
    ApiFollower,
    ApiContext,
    ValveApiCall,
)
from matches.management.tasks import MirrorMatches

# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
os.environ['http_proxy'] = ''
# End Patch


logger = logging.getLogger(__name__)


class AcquireHiddenLeagueGames(Task):

    """Deprecated.  A stupid hack to get 'secret' TI games."""

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
