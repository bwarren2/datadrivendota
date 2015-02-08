from itertools import chain as meld
from copy import deepcopy
from time import time as now
from celery import Task, chain
from players.models import Player
from teams.models import TeamDossier
from accounts.models import get_tracks
from teams.models import assemble_pros
from settings.base import ADDER_32_BIT
import logging

from datadrivendota.management.tasks import (
    BaseTask,
    ValveApiCall,
    ApiFollower,
    ApiContext,
)
from matches.management.tasks import CycleApiCall
# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
import os
os.environ['http_proxy'] = ''
# End Patch

logger = logging.getLogger(__name__)


class MirrorClientPersonas(BaseTask):

    def run(self):
        """
        Go through the users for whom update is True and group them into lists
        of 50.  The profile update API actually supports up to 100
        """
        list_send_length = 50
        users = Player.objects.filter(updated=True)
        tracked = get_tracks(users)

        teams = TeamDossier.objects.all()
        pros = assemble_pros(teams)

        track_list = meld(users, tracked)

        check_list = [user.steam_id for user in track_list]
        check_list.extend(pros)

        querylist = []

        for counter, user in enumerate(check_list, start=1):
            id_64_bit = str(user + ADDER_32_BIT)
            querylist.append(id_64_bit)

            # if our list is list_send_length long or we have reached the end
            if counter % list_send_length == 0 or counter == len(check_list):
                steamids = ",".join(querylist)
                vac = ValveApiCall()
                upp = UpdateClientPersonas()
                self.api_context.steamids = steamids
                pass_context = deepcopy(self.api_context)
                chain(vac.s(
                    mode='GetPlayerSummaries',
                    api_context=pass_context
                ), upp.s()).delay()
                querylist = []


class UpdateClientPersonas(ApiFollower):

    def run(self, urldata):
        """Make the avatar and persona facts of a profile match current."""
        # This options is present in the return code, but not needed here.
        # valveOpts = urldata['valveOpts']
        response = urldata['response']

        for pulled_player in response['players']:
            logger.info(
                "Updating "
                + pulled_player['personaname']
                + ","
                + str(pulled_player['steamid'])
            )
            # The PlayerSummaries call returns 64 bit ids.  It is super
            # annoying.
            id_32bit = int(pulled_player['steamid']) % ADDER_32_BIT

            player, created = Player.objects.get_or_create(steam_id=id_32bit)
            player.persona_name = pulled_player['personaname']
            player.profile_url = pulled_player['profileurl']
            player.avatar = pulled_player['avatar']
            player.avatar_medium = pulled_player['avatarmedium']
            player.avatar_full = pulled_player['avatarfull']
            player.save()


class MirrorPlayerData(BaseTask):

    def run(self):
        if self.api_context.account_id is None:
            logger.error("Needed an account id, had none, failed.")
        player = Player.objects.get_or_create(
            steam_id=self.api_context.account_id
        )[0]
        player.updated = True
        player.save()
        if self.api_context.matches_requested is None:
            self.api_context.matches_requested = 500
        self.api_context.start_scrape_time = now()
        self.api_context.last_scrape_time = player.last_scrape_time
        self.api_context.deepycopy = True
        if self.api_context.matches_desired is None:
            self.api_context.matches_desired = 500
        for skill in self.api_context.skill_levels:
            self.api_context.skill = skill

            vac = ValveApiCall()
            rpr = CycleApiCall()
            pass_context = deepcopy(self.api_context)
            chain(vac.s(
                mode='GetMatchHistory',
                api_context=pass_context
            ), rpr.s()).delay()


class MirrorProNames(Task):
    """Gets the pro name for each person in the current roster set"""

    def run(self):
        # Purge out the people that have pro names but are not on teams.
        ps = Player.objects.filter(player_0=None).filter(player_1=None)
        ps = ps.filter(player_2=None).filter(player_3=None)
        ps = ps.filter(player_4=None).filter(team_admin=None)
        ps = ps.exclude(pro_name=None).exclude(pro_name='')

        ps.update(pro_name=None)

        # Get the new names for people on teams.
        teams = TeamDossier.objects.all()
        pros = assemble_pros(teams)
        for p in pros:
            c = ApiContext()
            vac = ValveApiCall()
            c.AccountID = p
            upn = UpdateProNames()
            t = chain(
                vac.s(api_context=c, mode='GetPlayerOfficialInfo'), upn.s()
            )
            t.delay()


class UpdateProNames(ApiFollower):
    """
    Takes a ping to the official player database and updates that player's
    pro name
    """
    def run(self, urldata):
        player = Player.objects.get_or_create(
            steam_id=self.api_context.AccountID
            )[0]
        if self.result['Name'] == '':
            player.pro_name = None
            player.save()
        else:
            tag = self.result['TeamTag']
            name = self.result['Name']
            player.pro_name = '[' + tag + '] ' + name
            player.save()


class MirrorClientMatches(BaseTask):

    def run(self):
        """
        Go through the users for whom update is True and pull match histories
        since their last scrape time
        """
        users = Player.objects.filter(updated=True).select_related()
        tracked = get_tracks(users)
        check_list = meld(users, tracked)
        check_list = [user for user in check_list]

        for counter, user in enumerate(check_list, start=1):
            context = ApiContext()
            context.account_id = user.steam_id

            if self.api_context.matches_requested is None:
                context.matches_requested = 20
            else:
                context.matches_requested = self.api_context.matches_requested

            if self.api_context.matches_desired is None:
                context.matches_desired = 20
            else:
                context.matches_desired = self.api_context.matches_desired

            context.deepcopy = True
            context.start_scrape_time = now()
            context.last_scrape_time = user.last_scrape_time
            logger.info(context)
            vac = ValveApiCall()
            rpr = CycleApiCall()
            chain(vac.s(
                mode='GetMatchHistory',
                api_context=context
            ), rpr.s()).delay()
