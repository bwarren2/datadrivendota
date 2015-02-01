from celery import Task, chain
from matches.models import (
    Match,
    LobbyType,
    GameMode,
    LeaverStatus,
    PlayerMatchSummary,
    SkillBuild,
    AdditionalUnit,
    PickBan
)
from players.models import Player
from heroes.models import Ability, Hero
from items.models import Item
from leagues.models import League
from guilds.models import Guild
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


class MirrorMatches(Task):

    def run(self, matches=[], skill=None):
        for match in matches:
            logger.info("Requesting match {0}".format(match))
            c = ApiContext()
            if skill is not None:
                c.skill = skill
            c.matches_requested = 1
            c.matches_desired = 1
            c.refresh_records = True
            c.match_id = match
            c.refresh_records = True
            vac = ValveApiCall()
            um = UpdateMatch()
            c = chain(vac.s(api_context=c, mode='GetMatchDetails'), um.s())
            c.delay()


class UpdateMatch(ApiFollower):

    def run(self, data):
        """
        Uploads a match given the return of an API call.
        Only if the match does not exist are the player summaries imported;
        this will not correctly account for players that unanonymize their
        data. More code to the effect of "Look in the hero slot of the player
        you are searching for, see if it is anonymous, update if so" is
        needed; if urldata['status'] == 1: right now this just trawls for
        overall match data.
        """
        data = self.result

        kwargs = {
            'radiant_win': data['radiant_win'],
            'duration': data['duration'],
            'start_time': data['start_time'],
            'steam_id': data['match_id'],
            'match_seq_num': data['match_seq_num'],
            'tower_status_radiant': data['tower_status_radiant'],
            'tower_status_dire': data['tower_status_dire'],
            'barracks_status_radiant': data['barracks_status_radiant'],
            'barracks_status_dire': data['barracks_status_dire'],
            'cluster': data['cluster'],
            'first_blood_time': data['first_blood_time'],
            'lobby_type': LobbyType.objects.get_or_create(
                steam_id=data['lobby_type']
            )[0],
            'human_players': data['human_players'],
            'positive_votes': data['positive_votes'],
            'negative_votes': data['negative_votes'],
            'game_mode': GameMode.objects.get_or_create(
                steam_id=data['game_mode']
            )[0],
            'skill': self.api_context.skill,
        }
        try:

            league = League.objects.get_or_create(
                steam_id=data['leagueid']
                )[0]
            kwargs.update({'league': league})
        except KeyError:
            pass

        update = False
        try:
            match = Match.objects.get(steam_id=data['match_id'])
            if self.api_context.refresh_records:
                for key, value in kwargs.iteritems():
                    setattr(match, key, value)
                match.save()
                upload_match_summary(
                    players=data['players'],
                    parent_match=match,
                    refresh_records=self.api_context.refresh_records
                )
                update = True

        except Match.DoesNotExist:
            update = True
            match = Match.objects.create(**kwargs)
            match.save()
            upload_match_summary(
                players=data['players'],
                parent_match=match,
                refresh_records=self.api_context.refresh_records
            )

        if 'picks_bans' in data.keys() and update:
            for pickban in data['picks_bans']:
                datadict = {
                    'match': match,
                    'is_pick': pickban['is_pick'],
                    'hero': Hero.objects.get_or_create(
                        steam_id=pickban['hero_id']
                    )[0],
                    'team': pickban['team'],
                    'order': pickban['order'],

                }
                pb = PickBan.objects.get_or_create(
                    match=match,
                    order=pickban['order'],
                    defaults=datadict
                )[0]
                pb.save()

        if 'series_id' in data.keys() and update:
            match.series_id = data['series_id']

        if 'series_type' in data.keys() and update:
            match.series_type = data['series_type']

        if 'radiant_guild_id' in data.keys() and update:
            datadict = {
                'steam_id': data["radiant_guild_id"],
                'name': data["radiant_guild_name"],
                'logo': data["radiant_guild_logo"],
            }
            g = Guild.objects.get_or_create(
                steam_id=data["radiant_guild_id"],
                defaults=datadict
            )[0]
            match.radiant_guild = g

        if 'dire_guild_id' in data.keys() and update:
            datadict = {
                'steam_id': data["dire_guild_id"],
                'name': data["dire_guild_name"],
                'logo': data["dire_guild_logo"],
            }
            g = Guild.objects.get_or_create(
                steam_id=data["dire_guild_id"],
                defaults=datadict
            )[0]
            match.dire_guild = g

        if 'radiant_team_id' in data.keys() and update:
            radiant_team = Team.objects.get_or_create(
                steam_id=data['radiant_team_id']
                )[0]
            match.radiant_team = radiant_team
            match.radiant_team_complete = True \
                if data['radiant_team_id'] == 1 else False

        if 'dire_team_id' in data.keys() and update:
            dire_team = Team.objects.get_or_create(
                steam_id=data['dire_team_id']
                )[0]
            match.dire_team = dire_team
            match.dire_team_complete = True \
                if data['dire_team_id'] == 1 else False
        match.save()


def upload_match_summary(players, parent_match, refresh_records):
    """
    Populates the endgame summary data that is associated with a match
    and invokes the build parser.  This needs to be fixed for players that
    unanonymize by checking on hero_slot, ignoring player, and updating
    if new data has been included (in particular, which player we are
    talking about).
    """
    for player in players:
        # Bots do not have data assigned to them.  We have a fictitious
        # player and leaver status to hold this data.
        try:
            account_id = player['account_id']
            leaver_status = player['leaver_status']
        except KeyError:
            account_id = 0  # No acct ID means the player is a bot.
            leaver_status = -1
        kwargs = {
            'match': parent_match,
            'player': Player.objects.get_or_create(
                steam_id=account_id)[0],
            'leaver': LeaverStatus.objects.get_or_create(
                steam_id=leaver_status)[0],
            'player_slot': player['player_slot'],
            'hero': Hero.objects.get_or_create(
                steam_id=player['hero_id'],
                )[0],
            'item_0': Item.objects.get_or_create(steam_id=player['item_0'])[0],
            'item_1': Item.objects.get_or_create(steam_id=player['item_1'])[0],
            'item_2': Item.objects.get_or_create(steam_id=player['item_2'])[0],
            'item_3': Item.objects.get_or_create(steam_id=player['item_3'])[0],
            'item_4': Item.objects.get_or_create(steam_id=player['item_4'])[0],
            'item_5': Item.objects.get_or_create(steam_id=player['item_5'])[0],
            'kills': player['kills'],
            'deaths': player['deaths'],
            'assists': player['assists'],
            'gold': player['gold'],
            'last_hits': player['last_hits'],
            'denies': player['denies'],
            'gold_per_min': player['gold_per_min'],
            'xp_per_min': player['xp_per_min'],
            'gold_spent': player['gold_spent'],
            'hero_damage': player['hero_damage'],
            'tower_damage': player['tower_damage'],
            'hero_healing': player['hero_healing'],
            'level': player['level'],
        }
        try:
            pms = PlayerMatchSummary.objects.get(
                player_slot=player['player_slot'],
                match=parent_match
            )
            if refresh_records:
                for key, value in kwargs.iteritems():
                    setattr(pms, key, value)
                pms.save()
            playermatchsummary = pms
        except PlayerMatchSummary.DoesNotExist:
            playermatchsummary = PlayerMatchSummary.objects.get_or_create(
                **kwargs
            )[0]

        if 'ability_upgrades' in player.keys():
            for skillpick in player['ability_upgrades']:
                kwargs = {
                    'player_match_summary': playermatchsummary,
                    'ability': Ability.objects.get_or_create(
                        steam_id=skillpick['ability']
                    )[0],
                    'time': skillpick['time'],
                    'level': skillpick['level'],
                }
                SkillBuild.objects.get_or_create(**kwargs)

        if 'additional_units' in player.keys():
            for unit in player['additional_units']:
                kwargs = {
                    'player_match_summary': playermatchsummary,
                    'unit_name': unit['unitname'],
                    'item_0': Item.objects.get_or_create(
                        steam_id=unit['item_0']
                    )[0],
                    'item_1': Item.objects.get_or_create(
                        steam_id=unit['item_1']
                    )[0],
                    'item_2': Item.objects.get_or_create(
                        steam_id=unit['item_2']
                    )[0],
                    'item_3': Item.objects.get_or_create(
                        steam_id=unit['item_3']
                    )[0],
                    'item_4': Item.objects.get_or_create(
                        steam_id=unit['item_4']
                    )[0],
                    'item_5': Item.objects.get_or_create(
                        steam_id=unit['item_5']
                    )[0],
                }
                AdditionalUnit.objects.get_or_create(**kwargs)
