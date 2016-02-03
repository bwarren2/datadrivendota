import logging
from copy import deepcopy
from time import time
from celery import Task, chain

from django.conf import settings
from players.models import Player
from teams.models import Team
from teams.models import assemble_pros

from datadrivendota.management.tasks import (
    BaseTask,
    ValveApiCall,
    ApiFollower,
    ApiContext,
)
from matches.management.tasks import CycleApiCall


logger = logging.getLogger(__name__)


class MirrorClientPersonas(Task):

    def run(self):
        """
        Get valve player data for clients.

        Go through the users for whom update is True and group them into lists
        of 50.  The profile update API actually supports up to 100
        """
        list_send_length = 50
        users = Player.objects.filter(updated=True)

        teams = Team.objects.all()
        pros = assemble_pros(teams)

        check_list = [user.steam_id for user in users]
        check_list.extend(pros)

        querylist = []

        for counter, user in enumerate(check_list, start=1):
            id_64_bit = str(user + settings.ADDER_32_BIT)
            querylist.append(id_64_bit)

            # if our list is list_send_length long or we have reached the end
            if counter % list_send_length == 0 or counter == len(check_list):
                steamids = ",".join(querylist)
                vac = ValveApiCall()
                upp = UpdateClientPersonas()
                api_context = ApiContext()
                api_context.steamids = steamids
                chain(vac.s(
                    mode='GetPlayerSummaries',
                    api_context=api_context
                ), upp.s()).delay()
                querylist = []


class UpdateClientPersonas(ApiFollower):

    def run(self, api_context, json_data, response_code, url):
        """Make the avatar and persona facts of a profile match current."""
        # This options is present in the return code, but not needed here.
        # valveOpts = urldata['valveOpts']
        response = json_data['response']

        for pulled_player in response['players']:
            logger.info(
                "Updating {0}, {1}".format(
                    pulled_player['personaname'],
                    pulled_player['steamid']
                )
            )
            # The PlayerSummaries call returns 64 bit ids.  It is super
            # annoying.
            id_32bit = int(pulled_player['steamid']) % settings.ADDER_32_BIT

            player, created = Player.objects.get_or_create(steam_id=id_32bit)
            player.persona_name = pulled_player['personaname']
            player.profile_url = pulled_player['profileurl']
            player.avatar = pulled_player['avatar']
            player.avatar_medium = pulled_player['avatarmedium']
            player.avatar_full = pulled_player['avatarfull']
            player.save()


class MirrorPlayerData(BaseTask):

    """
    The major entry point to the system.

    Creates a player for recurring update and pulls in a bunch of information.

    @todo: refactor this with accounts refactor.
    """

    def run(self, api_context):
        if api_context.account_id is None:
            logger.error("Needed an account id, had none, failed.")
        player = Player.objects.get_or_create(
            steam_id=api_context.account_id
        )[0]
        player.updated = True
        player.save()
        if api_context.matches_requested is None:
            api_context.matches_requested = 500

        api_context.start_scrape_time = time()
        api_context.last_scrape_time = player.last_scrape_time
        api_context.deepycopy = True

        if api_context.matches_desired is None:
            api_context.matches_desired = 500
        for skill in api_context.skill_levels:
            api_context.skill = skill

            vac = ValveApiCall()
            rpr = CycleApiCall()
            pass_context = deepcopy(api_context)
            chain(vac.s(
                mode='GetMatchHistory',
                api_context=pass_context
            ), rpr.s()).delay()


class MirrorProNames(Task):

    """ Gets the pro name for each person in the current roster set. """

    def run(self):
        # Purge out the people that have pro names but are not on teams.
        ps = Player.objects.filter(player_0=None).filter(player_1=None)
        ps = ps.filter(player_2=None).filter(player_3=None)
        ps = ps.filter(player_4=None).filter(team_admin=None)
        ps = ps.exclude(pro_name=None).exclude(pro_name='')

        ps.update(pro_name=None)

        # Get the new names for people on teams.
        teams = Team.objects.all()
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

    """ Takes a ping to the official player database and update pro name. """

    def run(self, api_context, json_data, response_code, url):
        json_data = json_data['result']
        player = Player.objects.get_or_create(
            steam_id=api_context.AccountID
        )[0]

        if json_data['Name'] == '':
            player.pro_name = None
            player.save()
        else:
            tag = json_data['TeamTag']
            name = json_data['Name']
            player.pro_name = '[' + tag + '] ' + name
            player.save()


class MirrorClientMatches(Task):

    def run(self):
        """
        Get matches for clients.

        Go through the users for whom update is True and pull match histories
        since their last scrape time
        """
        users = Player.objects.filter(updated=True).select_related()
        check_list = [user for user in users]

        for counter, user in enumerate(check_list, start=1):

            context = ApiContext()
            context.account_id = user.steam_id
            context.matches_requested = settings.CLIENT_MATCH_COUNT
            context.matches_desired = settings.CLIENT_MATCH_COUNT
            context.start_scrape_time = time()
            context.last_scrape_time = user.last_scrape_time

            vac = ValveApiCall()
            rpr = CycleApiCall()
            chain(vac.s(
                mode='GetMatchHistory',
                api_context=context
            ), rpr.s()).delay()
