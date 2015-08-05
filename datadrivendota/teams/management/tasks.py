from time import time
from django.conf import settings
from celery import Task, chain
from matches.models import Match
from players.models import Player
from teams.models import Team
import logging
from datadrivendota.management.tasks import (
    ValveApiCall,
    ApiFollower,
    ApiContext
)

logger = logging.getLogger(__name__)


class MirrorRecentTeams(Task):

    """ Get new team data from matches.

    @todo: add scheduled matches for searching.
    """

    def run(self):
        matches = Match.objects.filter(skill=4).exclude(radiant_team=None)\
            .filter(start_time__gte=time() - settings.UPDATE_LAG_UTC)\
            .select_related('radiant_team__steam_id')
        teams = [m.radiant_team.steam_id for m in matches]

        matches = Match.objects.filter(skill=4).exclude(dire_team=None)\
            .filter(start_time__gte=time() - settings.UPDATE_LAG_UTC)\
            .select_related('dire_team__steam_id')
        teams.extend([m.dire_team.steam_id for m in matches])

        updatable = Team.objects.exclude(image_ugc=None).filter(
            valve_cdn_image=None
        )
        teams.extend([t.steam_id for t in updatable])

        teams = list(set(teams))
        logger.info("Updating {0} teams: {1}".format(len(teams), teams))
        for t in teams:
            c = ApiContext()
            c.refresh_records = True
            c.start_at_team_id = t
            c.teams_requested = 1
            vac = ValveApiCall()
            ul = UpdateTeam()
            c = chain(vac.s(api_context=c, mode='GetTeamInfoByTeamID'), ul.s())
            c.delay()


class MirrorTeamDetails(Task):

    """ Update a list of given teams. """

    def run(self, teams=None):

        if teams is None:
            teams = [t.steam_id for t in Team.objects.filter(name=None)]
        else:
            pass  # presume teams is a list of steam ids
        for t in teams:
            c = ApiContext()
            c.refresh_records = True
            c.start_at_team_id = t
            c.teams_requested = 1
            vac = ValveApiCall()
            ul = UpdateTeam()

            c = chain(vac.s(api_context=c, mode='GetTeamInfoByTeamID'), ul.s())
            c.delay()


class UpdateTeam(ApiFollower):

    """ Merge the data for a team into the DB. """

    def run(self, urldata):

        for team_data in self.result['teams']:
            team, created = Team.objects.get_or_create(
                steam_id=team_data['team_id']
            )
            try:
                if self.api_context.refresh_records:
                    mapping_dict = {
                        'name': 'name',
                        'tag': 'tag',
                        'created': 'time_created',
                        'logo': 'logo',
                        'logo_sponsor': 'logo_sponsor',
                        'country_code': 'country_code',
                        'url': 'url',
                        'games_played_with_current_roster':
                            'games_played_with_current_roster',
                    }
                    for internal, external in mapping_dict.iteritems():
                        if external in team_data.iterkeys():
                            setattr(team, internal, team_data.get(external))

                    map_team_players(team, team_data)
                    team.save()
            except Team.DoesNotExist:
                team = Team.objects.create(
                    name=team['name'],
                    tag=team['tag'],
                    created=team['time_created'],
                    logo_sponsor=team['logo_sponsor'],
                    logo=team['logo'],
                    country_code=team['country_code'],
                    url=team['url'],
                    games_played_with_current_roster=team[
                        'games_played_with_current_roster'
                    ],
                )
                map_team_players(team, team_data)
                if 'rating' in team.iterkeys():
                        setattr(team, 'rating', team.get('rating'))

                team.save()

            self._update_team_logos(team)

    def _update_team_logos(self, team):
        logo = team.logo
        if self._need_logo_update(logo):
            c = ApiContext()
            vac = ValveApiCall()
            c.ugcid = team.logo
            c.team_id = team.steam_id
            c.logo_type = 'team'

            utl = UpdateTeamLogo()

            if c.ugcid != 0:
                c = chain(
                    vac.s(api_context=c, mode='GetUGCFileDetails'), utl.s()
                )
                c.delay()
            else:
                err = "Disregarding ugc serach for {0}; no valid ugc (0 given)"
                logger.info(err.format(c.team_id))

        logo = team.logo_sponsor
        if self._need_logo_update(logo):
            c = ApiContext()
            vac = ValveApiCall()
            c.ugcid = team.logo
            c.team_id = team.steam_id
            c.logo_type = 'sponsor'

            utl = UpdateTeamLogo()

            c = chain(
                vac.s(api_context=c, mode='GetUGCFileDetails'), utl.s()
            )
            c.delay()

    def _need_logo_update(self, logo):
        return True
        return logo != 0 and logo is not None


class UpdateTeamLogo(ApiFollower):

    """ Merge a logo into the db. """

    def run(self, urldata):

        team = Team.objects.get(steam_id=self.api_context.team_id)
        url = urldata['data']['url']
        try:
            if self.api_context.logo_type == 'team':
                team.valve_cdn_image = url
                logger.debug(url)
            else:
                team.valve_cdn_sponsor_image = url
            team.save()

        # If we fail, put in a placeholder and freak.
        except Exception:
            if self.api_context.logo_type == 'team':
                team.valve_cdn_image = url
                print url
            else:
                team.valve_cdn_sponsor_image = url
            raise


def map_team_players(team, team_data):
    """ A convenience layer to the data attr names. """
    player_field_mapping_dict = {
        'player_0': 'player_0_account_id',
        'player_1': 'player_1_account_id',
        'player_2': 'player_2_account_id',
        'player_3': 'player_3_account_id',
        'player_4': 'player_4_account_id',
        'admin': 'admin_account_id',
    }
    for internal, external in player_field_mapping_dict.iteritems():
        if external in team_data.iterkeys():
            p = Player.objects.get_or_create(
                steam_id=team_data.get(external)
            )[0]
            setattr(team, internal, p)
