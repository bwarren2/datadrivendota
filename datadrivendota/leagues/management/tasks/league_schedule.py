""" Tasks to manage leagues. """
import os
import logging
from celery import Task, chain

from leagues.models import League
from teams.models import Team
from leagues.models import ScheduledMatch
from datadrivendota.management.tasks import (
    ApiFollower,
    ApiContext,
    ValveApiCall,
)

# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
os.environ['http_proxy'] = ''
# End Patch


logger = logging.getLogger(__name__)


class MirrorLeagueSchedule(Task):

    """ Get the match schedules and update. """

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

    """ Reflect current schedule in matches. """

    def run(self, api_context, json_data, response_code, url):
        logger.info("Saving the schedule")
        data = self.clean_urldata(json_data)
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
        """ Strip out request-level response from valve. """
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
