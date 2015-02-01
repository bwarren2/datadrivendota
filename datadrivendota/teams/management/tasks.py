import urllib2
from uuid import uuid4
from celery import Task, chain
from django.core.files import File
from django.utils.text import slugify
from matches.models import (
    Match,
)
from players.models import Player
from teams.models import Team, TeamDossier
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
            ul = UploadTeam()
            c = chain(vac.s(api_context=c, mode='GetTeamInfoByTeamID'), ul.s())
            c.delay()


class MirrorTeamDossiers(Task):

    def run(self):
        teams = Team.objects.filter(teamdossier=None)
        for t in teams:
            c = ApiContext()
            c.refresh_records = True
            c.start_at_team_id = t.steam_id
            c.teams_requested = 1
            vac = ValveApiCall()
            ul = UploadTeam()
            c = chain(vac.s(api_context=c, mode='GetTeamInfoByTeamID'), ul.s())
            c.delay()


class UploadTeam(ApiFollower):
    def run(self, urldata):
        for team in self.result['teams']:
            t, created = Team.objects.get_or_create(
                steam_id=team['team_id']
                )
            try:
                teamdoss = TeamDossier.objects.get(
                    team=t,
                    )
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
                        if external in team.iterkeys():
                            setattr(teamdoss, internal, team.get(external))

                    map_team_players(teamdoss, team)
                    teamdoss.save()

                    update_team_logos(t)

                    # c = ApiContext()
                    # utl = UpdateTeamLogos()
                    # utl.s(api_context=c, team_steam_id=t.steam_id).delay()

            except TeamDossier.DoesNotExist:
                teamdoss = TeamDossier.objects.create(
                    team=t,
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
                map_team_players(teamdoss, team)
                if 'rating' in team.iterkeys():
                        setattr(teamdoss, 'rating', team.get('rating'))

                teamdoss.save()
                update_team_logos(t)


class UpdateTeamLogo(ApiFollower):
    def run(self, urldata):
        team = Team.objects.get(steam_id=self.api_context.team_id)
        URL = urldata['data']['url']
        try:
            imgdata = urllib2.urlopen(URL, timeout=5)
            with open('%s.png' % str(uuid4()), 'w+') as f:
                f.write(imgdata.read())
            filename = slugify(team.teamdossier.name) + '.png'
            if self.api_context.logo_type == 'team':
                team.teamdossier.logo_image.save(
                    filename, File(open(f.name))
                    )
            else:
                team.teamdossier.logo_sponsor_image.save(
                    filename, File(open(f.name))
                )
            os.remove(f.name)

        # If we fail, put in a placeholder and freak.
        except Exception:
                filename = slugify(team.teamdossier.name)+'_logo.png'
                URL = ('https://s3.amazonaws.com/datadrivendota'
                       '/images/blank-logo.png')
                imgdata = urllib2.urlopen(URL, timeout=5)
                with open('%s.png' % str(uuid4()), 'w+') as f:
                    f.write(imgdata.read())

                if self.api_context.logo_type == 'team':
                    team.teamdossier.logo_image.save(
                        filename, File(open(f.name))
                        )
                else:
                    team.teamdossier.logo_sponsor_image.save(
                        filename, File(open(f.name))
                    )
                os.remove(f.name)
                raise


def update_team_logos(team):
    # Refresh the logo
    logo = team.teamdossier.logo
    teamdoss = team.teamdossier
    if logo != 0 and logo is not None:
        c = ApiContext()
        vac = ValveApiCall()
        c.ugcid = teamdoss.logo
        c.team_id = teamdoss.team.steam_id
        c.logo_type = 'team'

        utl = UpdateTeamLogo()

        c = chain(
            vac.s(api_context=c, mode='GetUGCFileDetails'), utl.s()
        )
        c.delay()

    logo = team.teamdossier.logo_sponsor
    if logo != 0 and logo is not None:
        c = ApiContext()
        vac = ValveApiCall()
        c.ugcid = teamdoss.logo
        c.team_id = teamdoss.team.steam_id
        c.logo_type = 'sponsor'

        utl = UpdateTeamLogo()

        c = chain(
            vac.s(api_context=c, mode='GetUGCFileDetails'), utl.s()
        )
        c.delay()


def map_team_players(teamdoss, team):
    player_field_mapping_dict = {
        'player_0': 'player_0_account_id',
        'player_1': 'player_1_account_id',
        'player_2': 'player_2_account_id',
        'player_3': 'player_3_account_id',
        'player_4': 'player_4_account_id',
        'admin': 'admin_account_id',
    }
    for internal, external in player_field_mapping_dict.iteritems():
        if external in team.iterkeys():
            p = Player.objects.get_or_create(steam_id=team.get(external))[0]
            setattr(teamdoss, internal, p)
