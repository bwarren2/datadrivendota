import urllib2
from datetime import datetime
from uuid import uuid4
from celery import Task, chain
from django.core.files import File
from django.utils.text import slugify
from matches.models import (
    Match,
)
from players.models import Player
from teams.models import Team
import logging

from datadrivendota.management.tasks import (
    ValveApiCall,
    ApiFollower,
    ApiContext
)

# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
import os
os.environ['http_proxy'] = ''
# End Patch


logger = logging.getLogger(__name__)


class MirrorTeams(Task):
    """ Get new team data from matches. """
    def run(self):
        matches = Match.objects.filter(skill=4).exclude(radiant_team=None)\
            .select_related('radiant_team__steam_id')
        teams = [m.radiant_team.steam_id for m in matches]

        matches = Match.objects.filter(skill=4).exclude(dire_team=None)\
            .select_related('dire_team__steam_id')
        teams.extend([m.dire_team.steam_id for m in matches])
        teams = list(set(teams))
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
        logger.info("Testing!")
        if self._need_logo_update(logo):
            logger.info("Passed test!")
            c = ApiContext()
            vac = ValveApiCall()
            c.ugcid = team.logo
            c.team_id = team.steam_id
            c.logo_type = 'team'

            utl = UpdateTeamLogo()

            c = chain(
                vac.s(api_context=c, mode='GetUGCFileDetails'), utl.s()
            )
            c.delay()

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
    def run(self, urldata):
        logger.error(urldata)
        if urldata['status'] == 'FAILURE':
            logger.error('FAILBOAT')
            return False
        team = Team.objects.get(steam_id=self.api_context.team_id)
        URL = urldata['data']['url']
        try:
            # imgdata = urllib2.urlopen(URL, timeout=5)
            # with open('%s.png' % str(uuid4()), 'w+') as f:
            #     foo = imgdata.read()
            #     print foo
            #     f.write(foo)
            # filename = slugify(team.name) + '.png'
            if self.api_context.logo_type == 'team':
                #     team.logo_image.save(
                #         filename, File(open(f.name))
                #         )
                team.valve_cdn_image = URL
                print URL
            else:
                # team.logo_sponsor_image.save(
                #     filename, File(open(f.name))
                # )
                team.valve_cdn_sponsor_image = URL

            # os.remove(f.name)
            team.save()

        # If we fail, put in a placeholder and freak.
        except Exception:
                filename = slugify(team.name)+'_logo.png'
                URL = ('https://s3.amazonaws.com/datadrivendota'
                       '/images/blank-logo.png')
                imgdata = urllib2.urlopen(URL, timeout=5)
                with open('%s.png' % str(uuid4()), 'w+') as f:
                    f.write(imgdata.read())

                if self.api_context.logo_type == 'team':
                    team.logo_image.save(
                        filename, File(open(f.name))
                        )
                    team.valve_cdn_image = URL
                else:
                    team.logo_sponsor_image.save(
                        filename, File(open(f.name))
                    )
                    team.valve_cdn_sponsor_image = URL
                os.remove(f.name)
                raise

    def failout(self):
        logger.error("I failed :( {0}".format(repr(self.api_context)))


def update_team_logos(team):
    """
    DEPRECATED

    Refresh the logo
    """
    logo = team.logo
    if logo != 0 and logo is not None:
        c = ApiContext()
        vac = ValveApiCall()
        c.ugcid = team.logo
        c.team_id = team.steam_id
        c.logo_type = 'team'

        utl = UpdateTeamLogo()

        c = chain(
            vac.s(api_context=c, mode='GetUGCFileDetails'), utl.s()
        )
        c.delay()

    logo = team.logo_sponsor
    if logo != 0 and logo is not None:
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


def map_team_players(team, team_data):
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
