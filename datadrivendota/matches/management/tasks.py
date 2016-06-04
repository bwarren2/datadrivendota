""" Tasks to manage match-related data. """
import logging
from celery import Task, chain
from time import time as now
from copy import deepcopy
from datetime import datetime, timedelta

from django.utils import timezone
from django.db.models import Min, Max, Count
from django.conf import settings

from matches.models import (
    Match,
    LobbyType,
    GameMode,
    LeaverStatus,
    PlayerMatchSummary,
    SkillBuild,
    AdditionalUnit,
    PickBan,
)
from datadrivendota.utilities import error_email
from players.models import Player
from heroes.models import Ability, Hero
from items.models import Item
from leagues.models import League, LiveMatch
from guilds.models import Guild
from teams.models import Team
from datadrivendota.management.tasks import (
    ValveApiCall,
    ApiFollower,
    ApiContext
)

logger = logging.getLogger(__name__)


class MirrorMatches(Task):

    """ Get the details of a list of matches. """

    def run(self, matches=[], skill=None):
        """ Spin each match into an update call & response. """
        for match in matches:
            logger.info("Requesting match {0}".format(match))
            c = ApiContext()
            if skill is not None:
                c.skill = skill
            c.matches_requested = 1
            c.matches_desired = 1
            c.refresh_records = True
            c.match_id = match
            vac = ValveApiCall()
            um = UpdateMatch()
            c = chain(vac.s(api_context=c, mode='GetMatchDetails'), um.s())
            c.delay()


class MirrorRecentMatches(Task):

    """ All the live games that have happened recently should come in. """

    def run(self, matches=[], skill=None):
        recent_live = set(
            LiveMatch.objects.filter(
                created_at__lte=timezone.now() - timedelta(
                    minutes=settings.LIVE_MATCH_LOOKBACK_MINUTES
                )
            )
            .values_list('steam_id', flat=True)
        )
        MirrorMatches().delay(matches=list(recent_live))


class UpdateMatch(ApiFollower):

    """ Reflect the match detail response in our database. """

    def run(self, api_context, json_data, response_code, url):
        """
        Upload a match given the return of an API call.

        Only if the match does not exist are the player summaries imported;
        this will not correctly account for players that unanonymize their
        data. More code to the effect of "Look in the hero slot of the player
        you are searching for, see if it is anonymous, update if so" is
        needed; if urldata['status'] == 1: right now this just trawls for
        overall match data.
        """
        if 'result' not in json_data:
            self.fail_match(api_context, json_data, response_code, url)

        else:
            data = json_data['result']
            if 'error' in data:
                self.error_match(
                    api_context, data['error'], response_code, url
                )
            else:
                self.update_match(api_context, data, response_code, url)

        # The downstream parsing tasks use this.
        return api_context

    def fail_match(self, api_context, json_data, response_code, url):
        logger.warning("Got fake data: {0}, {1}, {2}, {3}".format(
            api_context, json_data, response_code, url
        ))

    def error_match(self, api_context, error, response_code, url):
        not_found = error == 'Match ID not found'
        is_practice = error == (
            'Practice matches are not available via GetMatchDetails'
        )

        if not_found:
            logger.info(
                'Match ID {0} not found'.format(api_context.match_id)
            )
        elif is_practice:
            logger.info(
                'Match ID {0} was a practice match, not recorded'.format(
                    api_context.match_id
                )
            )
        else:
            logging.error("{0}.  Context:{1}".format(
                error, api_context)
            )

        # Do logging on associated livematch
        try:
            lm = LiveMatch.objects.get(
                steam_id=api_context.match_id
            )
            lm.failed = True
            lm.save()
        except LiveMatch.DoesNotExist:
            logging.info(
                'No live match to fail. ({0})'.format(
                    api_context.match_id
                )
            )

    def update_match(self, api_context, data, response_code, url):

        match = self.create_match(data, api_context)

        self.create_pickbans(data, match)

        match = self.merge_series(data, match)

        self.create_guilds(data, match)
        match = self.merge_guilds(data, match)

        self.create_teams(data, match)
        match = self.merge_teams(data, match)

        self.create_league(data, match)
        match = self.merge_league(data, match)

        match.save()

    def create_pickbans(self, data, match):
        if 'picks_bans' in data.keys():
            for idx, pickban in enumerate(data['picks_bans']):
                inferred_order = pickban.get('order', idx)
                datadict = {
                    'match': match,
                    'is_pick': pickban['is_pick'],
                    'hero': Hero.objects.get_or_create(
                        steam_id=pickban['hero_id']
                    )[0],
                    'team': pickban['team'],
                    'order': inferred_order,
                }
                pb = PickBan.objects.get_or_create(
                    match=match,
                    order=inferred_order,
                    defaults=datadict
                )[0]
                pb.save()

    def merge_series(self, data, match):
        if 'series_id' in data.keys():
            match.series_id = data['series_id']

        if 'series_type' in data.keys():
            match.series_type = data['series_type']

        return match

    def create_guilds(self, data, match):
        if is_useful_key(data, 'radiant_guild_id'):
            datadict = {
                'steam_id': data["radiant_guild_id"],
                'name': data["radiant_guild_name"],
                'logo': data["radiant_guild_logo"],
            }
            Guild.objects.get_or_create(
                steam_id=data["radiant_guild_id"],
                defaults=datadict
            )[0]

        if is_useful_key(data, 'dire_guild_id'):
            datadict = {
                'steam_id': data["dire_guild_id"],
                'name': data["dire_guild_name"],
                'logo': data["dire_guild_logo"],
            }
            Guild.objects.get_or_create(
                steam_id=data["dire_guild_id"],
                defaults=datadict
            )[0]

    def merge_guilds(self, data, match):
        if is_useful_key(data, 'radiant_guild_id'):
            g = Guild.objects.get(
                steam_id=data["radiant_guild_id"],
            )
            match.radiant_guild = g

        if is_useful_key(data, 'dire_guild_id'):
            g = Guild.objects.get(
                steam_id=data["dire_guild_id"],
            )
            match.dire_guild = g

        return match

    def create_teams(self, data, match):
        if is_useful_key(data, 'radiant_team_id'):
            Team.objects.get_or_create(
                steam_id=data['radiant_team_id']
            )[0]

        if is_useful_key(data, 'dire_team_id'):
            Team.objects.get_or_create(
                steam_id=data['dire_team_id']
            )[0]

    def merge_teams(self, data, match):

        if is_useful_key(data, 'radiant_team_id'):
            radiant_team = Team.objects.get(
                steam_id=data['radiant_team_id']
            )
            match.radiant_team = radiant_team
            match.radiant_team_complete = data['radiant_team_complete'] == 1

        if is_useful_key(data, 'dire_team_id'):
            dire_team = Team.objects.get(
                steam_id=data['dire_team_id']
            )
            match.dire_team = dire_team
            match.dire_team_complete = data['dire_team_complete'] == 1

        return match

    def create_league(self, data, match):
        if 'leagueid' in data.keys():
            League.objects.get_or_create(
                steam_id=data['leagueid']
            )[0]

    def merge_league(self, data, match):

        if 'leagueid' in data.keys():
            league = League.objects.get(
                steam_id=data['leagueid']
            )
            match.league = league

        return match

    def create_match(self, data, api_context):
        kwargs = {
            'radiant_win': data.get('radiant_win', None),
            'duration': data['duration'],
            'start_time': data['start_time'],
            'steam_id': data['match_id'],
            'match_seq_num': data['match_seq_num'],
            'tower_status_radiant': data['tower_status_radiant'],
            'tower_status_dire': data['tower_status_dire'],
            'barracks_status_radiant': data['barracks_status_radiant'],
            'barracks_status_dire': data['barracks_status_dire'],
            'cluster': data['cluster'],
            'replay_salt': str(data.get('replay_salt', None)),
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
            'skill': api_context.skill,
        }

        try:
            match = Match.objects.get(steam_id=data['match_id'])
            for key, value in kwargs.iteritems():
                setattr(match, key, value)
            match.save()
            upload_match_summary(
                players=data['players'],
                parent_match=match,
                refresh_records=api_context.refresh_records
            )

        except Match.DoesNotExist:
            print kwargs
            match = Match.objects.create(**kwargs)
            match.save()
            upload_match_summary(
                players=data['players'],
                parent_match=match,
                refresh_records=api_context.refresh_records
            )

        return match


def upload_match_summary(players, parent_match, refresh_records):
    """
    Populate the endgame summary data for a match.

    This needs to be fixed for players that
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
            'gold': player.get('gold', None),
            'last_hits': player['last_hits'],
            'denies': player['denies'],
            'gold_per_min': player['gold_per_min'],
            'xp_per_min': player['xp_per_min'],
            'gold_spent': player.get('gold_spent', None),
            'hero_damage': player.get('hero_damage', None),
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


class UpdateMatchValidity(Task):

    """Check for match validity and update accordingly."""

    def run(self):
        """ Update match validity. """
        self.update_validity()

    def update_validity(self):
        """ Select the match set to update and call processing. """
        unprocessed = Match.objects.filter(validity=Match.UNPROCESSED)
        self.process_matches(unprocessed)

        a = datetime.utcnow() - timedelta(days=settings.LOOKBACK_UPDATE_DAYS)
        unprocessed = Match.objects.filter(
            start_time__gte=a.strftime('%s')
        )
        self.process_matches(unprocessed)

    def process_matches(self, unprocessed):
        """ Apply filters to sort match validity. """
        if unprocessed.exists():
            max_id = unprocessed.aggregate(Max('id'))['id__max']
            min_id = unprocessed.aggregate(Min('id'))['id__min']

            def assign_tournament_level(unprocessed):
                unprocessed.filter(league__steam_id__gt=0).update(
                    skill=4
                )

            def tournament(unprocessed):

                # Mainly 1v1 practices
                unprocessed.filter(human_players__lt=10).update(
                    validity=Match.UNCOUNTED
                )

                # Failure to load
                unprocessed.filter(
                    playermatchsummary__hero__name=''
                ).update(
                    validity=Match.UNCOUNTED
                )

                unprocessed.filter(
                    playermatchsummary__hero__name='Blank'
                ).update(
                    validity=Match.UNCOUNTED
                )

                unprocessed.filter(
                    human_players=10,
                ).exclude(
                    playermatchsummary__hero__name=''
                ).update(validity=Match.LEGIT)

            def too_short(unprocessed):
                matches = unprocessed.filter(
                    duration__lte=settings.MIN_MATCH_LENGTH
                )
                matches.update(validity=Match.UNCOUNTED)

            # Games that do not have ten match summaries are uncounted.
            def player_count(unprocessed):
                ms = unprocessed.annotate(Count('playermatchsummary'))
                ms = ms.filter(playermatchsummary__count__lt=10)
                keys = ms.values_list('pk', flat=True)
                ms = unprocessed.filter(pk__in=keys)
                ms.update(validity=Match.UNCOUNTED)

            # Games against bots do not count.
            def human_players(unprocessed):
                ms = unprocessed.filter(human_players__lt=10)
                ms.update(validity=Match.UNCOUNTED)

            # Games with leavers do not count.
            def leavers(unprocessed):
                ms = unprocessed.filter(
                    playermatchsummary__leaver__steam_id__gt=1
                )
                ms.update(validity=Match.UNCOUNTED)

            # Only traditional game modes count.
            def game_mode_check(unprocessed):
                ms = unprocessed.exclude(
                    lobby_type__steam_id__in=[0, 2, 6, 7]
                )
                ms.update(validity=Match.UNCOUNTED)

            # Everything we did not just exclude is valid.
            def legitimize(unprocessed, max_id, min_id):
                ms = Match.objects.exclude(
                    id__gt=max_id,
                    id__lt=min_id
                )
                ms = ms.filter(validity=Match.UNPROCESSED)
                ms.update(validity=Match.LEGIT)

            assign_tournament_level(unprocessed)
            # Tournament matches get their own special handling.
            tournament_matches = unprocessed.filter(skill=4)
            tournament(tournament_matches)

            unprocessed = unprocessed.exclude(skill=4)

            # Mark bad matches
            too_short(unprocessed)
            player_count(unprocessed)
            human_players(unprocessed)
            leavers(unprocessed)
            game_mode_check(unprocessed)

            # Mark everything else as alright.
            legitimize(unprocessed, max_id, min_id)
        else:
            pass  # We got passed an empty match set to process.


class CheckMatchIntegrity(Task):

    """ Complain if derived features of matches look wrong. """

    def run(self):
        """ Select the match set to update. """
        radiant_badness = PlayerMatchSummary.objects.filter(
            match__radiant_win=True,
            player_slot__lte=5,
            is_win=False
        )
        if len(radiant_badness) != 0:
            error_email(
                'Database alert!',
                'We have denormalization for radiant players and iswin=False'
            )

        not_main_event_ti5 = Match.objects.filter(
            start_time__lte=1437980497,  # Magic time for the earlier stages
            league__steam_id=2733  # TI5 league id
        ).count()
        if not_main_event_ti5 != 0:
            error_email(
                'Database alert!',
                'We have reimported the not-main-event TI5 games.'
                'This muddies the data for that very important league.'
                'You probably want to delete them.'
            )

        dire_badness = PlayerMatchSummary.objects.filter(
            match__radiant_win=True,
            player_slot__gte=5,
            is_win=True
        )
        if len(dire_badness) != 0:
            (
                'Database alert!',
                'We have denormalization for dire players and iswin=True'
            )
        league_tier_badness = League.objects.filter(tier=None).count()
        if league_tier_badness != 0:
            (
                'Database alert!',
                'There are leagues with no tier, which should not happen.'
            )
        league_image_badness = League.objects.filter(
            stored_image=None
        ).count()
        if league_image_badness != 0:
            (
                'Database alert!',
                'There are leagues with no image, which should not happen.'
            )


class CycleApiCall(ApiFollower):

    """
    Recycle an API context to dig deeper into match results.

    Only supports get match history right now,
    but that is the only API that really leans on repeated calls.
    """

    def run(self, api_context, json_data, response_code, url):
        """ Ping the valve API to get match data & spawns new tasks. """
        # Validate
        if json_data:
            json_data = json_data['result']
            if json_data['status'] == 15:
                logger.warning(
                    "Could not pull data. {0}  disallowed it.".format(
                        api_context.account_id
                    )
                )
                return True

            elif json_data['status'] == 1:
                # Spawn a bunch of match detail queries

                logger.info("Spawning")

                self.spawn_detail_calls(json_data, api_context)

                logger.info("Checking for more results")
                if self.more_results_left(json_data, api_context):
                    self.rebound(json_data, api_context)

                # Successful closeout
                else:
                    logger.info("Cleaning up")
                    self.cleanup(api_context)
                return True
            else:
                logger.error(
                    "Unhandled status: {0}".format(
                        json_data['status']
                    )
                )
                return True
        else:
            logger.warning("Empty json for {0}".format(url))

    def spawn_detail_calls(self, json_data, api_context):
        """ Make match detail calls for each match. """
        for result in json_data['matches']:
            api_context.processed += 1
            if api_context.processed <= api_context.matches_desired:

                logger.info(
                    "{0}: {1} done, {2} wanted, doing: {3}".format(
                        api_context.account_id,
                        api_context.processed,
                        api_context.matches_desired,
                        api_context.processed <=
                        api_context.matches_desired
                    )
                )

                vac = ValveApiCall()
                um = UpdateMatch()
                api_context.match_id = result['match_id']
                pass_context = deepcopy(api_context)
                chain(vac.s(
                    mode='GetMatchDetails',
                    api_context=pass_context
                ), um.s()).delay()

    def more_results_left(self, json_data, api_context):
        """ Evaluate if more matches need to be queried. """
        if (json_data['results_remaining'] != 0) \
                and api_context.processed < \
                api_context.matches_desired:

            logger.info(
                (
                    "Did {0} of {1} for {2}. {3} left.  \n "
                    "Logic: remaining: {4}, "
                ).format(
                    api_context.processed,
                    api_context.matches_desired,
                    api_context.account_id,
                    json_data['results_remaining'],
                    not (json_data['results_remaining'] == 0),

                )
            )
            return True

        else:

            logger.info(
                "Did {0} of {1} for {2}. {3} left.  Done.".format(
                    api_context.processed,
                    api_context.matches_desired,
                    api_context.account_id,
                    json_data['results_remaining']
                )
            )

            return False

    # Until the date_max problem is fixed, date_max cannot work.
    def rebound(self, json_data, api_context):
        """ Re-hit the match history list for remaining matches. """
        logger.info("Rebounding")
        api_context.start_at_match_id = json_data[
            'matches'
        ][-1]['match_id']
        api_context.date_max = None

        vac = ValveApiCall()
        rpr = CycleApiCall()
        pass_context = deepcopy(api_context)
        chain(vac.s(
            mode='GetMatchHistory',
            api_context=pass_context
        ), rpr.s()).delay()

    def cleanup(self, api_context):
        """ Do maintenance for if we were focusing on a player. """
        if api_context.account_id is not None:
            try:
                player = Player.objects.get(
                    steam_id=api_context.account_id
                )
                if api_context.start_scrape_time:
                    new_last_scrape = api_context.start_scrape_time
                else:
                    new_last_scrape = now()
                player.last_scrape_time = new_last_scrape
                player.save()
            except Player.DoesNotExist:
                logger.error(
                    "ERROR! Player does not exist {0}".format(
                        api_context.account_id
                    )
                )

def is_useful_key(data, key):
    return key in data.keys() and data[key] is not None
