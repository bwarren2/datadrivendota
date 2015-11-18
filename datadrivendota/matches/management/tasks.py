""" Tasks to manage match-related data. """
import json
import logging
from celery import Task, chain
from time import time as now
from copy import deepcopy
from datetime import datetime, timedelta

from django.core.files import File
from utils import gzip_str
from io import BytesIO
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
from accounts.models import MatchRequest

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
from utils import gunzip_str

# Patch for <urlopen error [Errno -2] Name or service not known in urllib2
import os
os.environ['http_proxy'] = ''
# End Patch


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

    def run(self, data):
        """
        Upload a match given the return of an API call.

        Only if the match does not exist are the player summaries imported;
        this will not correctly account for players that unanonymize their
        data. More code to the effect of "Look in the hero slot of the player
        you are searching for, see if it is anonymous, update if so" is
        needed; if urldata['status'] == 1: right now this just trawls for
        overall match data.
        """
        data = self.result
        if 'error' in data:

            if data['error'] == 'Match ID not found':
                logger.warning(
                    'Match ID {0} not found'.format(self.api_context.match_id)
                )
            elif data['error'] == 'Practice matches are not available via GetMatchDetails':
                logger.warning(
                    'Match ID {0} was a practice match, not recorded'.format(
                        self.api_context.match_id
                    )
                )
            else:
                logging.error("{0}.  Context:{1}".format(
                    data['error'], self.api_context)
                )


            # Do logging on associated livematch
            try:
                lm = LiveMatch.objects.get(
                    steam_id=self.api_context.match_id
                )
                lm.failed = True
                lm.save()
            except:
                logging.warning(
                    'No live match to fail. ({0})'.format(
                        self.api_context.match_id
                    )
                )

        else:
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

            try:
                match = Match.objects.get(steam_id=data['match_id'])
                for key, value in kwargs.iteritems():
                    setattr(match, key, value)
                match.save()
                upload_match_summary(
                    players=data['players'],
                    parent_match=match,
                    refresh_records=self.api_context.refresh_records
                )

            except Match.DoesNotExist:
                match = Match.objects.create(**kwargs)
                match.save()
                upload_match_summary(
                    players=data['players'],
                    parent_match=match,
                    refresh_records=self.api_context.refresh_records
                )

            if 'picks_bans' in data.keys():
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

            if 'series_id' in data.keys():
                match.series_id = data['series_id']

            if 'series_type' in data.keys():
                match.series_type = data['series_type']

            if 'radiant_guild_id' in data.keys():
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

            if 'dire_guild_id' in data.keys():
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

            if 'radiant_team_id' in data.keys():
                radiant_team = Team.objects.get_or_create(
                    steam_id=data['radiant_team_id']
                )[0]
                match.radiant_team = radiant_team
                match.radiant_team_complete = True \
                    if data['radiant_team_id'] == 1 else False

            if 'dire_team_id' in data.keys():
                dire_team = Team.objects.get_or_create(
                    steam_id=data['dire_team_id']
                )[0]
                match.dire_team = dire_team
                match.dire_team_complete = True \
                    if data['dire_team_id'] == 1 else False
            match.save()

            return self.api_context


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

    def run(self, urldata):
        """ Ping the valve API to get match data & spawns new tasks. """
        # Validate
        if self.result['status'] == 15:
            logger.warning(
                "Could not pull data. "
                + str(self.api_context.account_id)
                + " disallowed it. "
            )
            p = Player.objects.get(steam_id=self.api_context.account_id)
            p.updated = False
            p.save()
            return True

        elif self.result['status'] == 1:
            # Spawn a bunch of match detail queries

            logger.info("Spawning")

            self.spawn_detail_calls()

            logger.info("Checking for more results")
            if self.more_results_left():
                self.rebound()

            # Successful closeout
            else:
                logger.info("Cleaning up")
                self.cleanup()
            return True
        else:
            logger.error(
                "Unhandled status: {0}".format(
                    str(self.result['status'])
                )
            )
            return True

    def spawn_detail_calls(self):
        """ Make match detail calls for each match. """
        for result in self.result['matches']:
            self.api_context.processed += 1
            if self.api_context.processed <= self.api_context.matches_desired:

                logger.info(
                    "{0}: {1} done, {2} wanted, doing: {3}".format(
                        self.api_context.account_id,
                        self.api_context.processed,
                        self.api_context.matches_desired,
                        self.api_context.processed <=
                        self.api_context.matches_desired
                    )
                )

                vac = ValveApiCall()
                um = UpdateMatch()
                self.api_context.match_id = result['match_id']
                pass_context = deepcopy(self.api_context)
                chain(vac.s(
                    mode='GetMatchDetails',
                    api_context=pass_context
                ), um.s()).delay()

    def more_results_left(self):
        """ Evaluate if more matches need to be queried. """
        if (self.result['results_remaining'] != 0) \
                and self.api_context.processed < \
                self.api_context.matches_desired:

            logger.info(
                (
                    "Did {0} of {1} for {2}. {3} left.  \n "
                    "Logic: remaining: {4}, "
                ).format(
                    self.api_context.processed,
                    self.api_context.matches_desired,
                    self.api_context.account_id,
                    self.result['results_remaining'],
                    not (self.result['results_remaining'] == 0),

                )
            )
            return True

        else:

            logger.info(
                "Did {0} of {1} for {2}. {3} left.  Done.".format(
                    self.api_context.processed,
                    self.api_context.matches_desired,
                    self.api_context.account_id,
                    self.result['results_remaining']
                )
            )

            return False

    # Until the date_max problem is fixed, date_max cannot work.
    def rebound(self):
        """ Re-hit the match history list for remaining matches. """
        logger.info("Rebounding")
        self.api_context.start_at_match_id = self.result[
            'matches'
        ][-1]['match_id']
        self.api_context.date_max = None

        vac = ValveApiCall()
        rpr = CycleApiCall()
        pass_context = deepcopy(self.api_context)
        chain(vac.s(
            mode='GetMatchHistory',
            api_context=pass_context
        ), rpr.s()).delay()

    def cleanup(self):
        """ Do maintenance for if we were focusing on a player. """
        if self.api_context.account_id is not None:
            try:
                player = Player.objects.get(
                    steam_id=self.api_context.account_id
                )
                if self.api_context.start_scrape_time:
                    new_last_scrape = self.api_context.start_scrape_time
                else:
                    new_last_scrape = now()
                player.last_scrape_time = new_last_scrape
                player.save()
            except Player.DoesNotExist:
                logger.error(
                    "ERROR! Player does not exist {0}".format(
                        self.api_context.account_id
                    )
                )


class UpdatePmsReplays(Task):

    def run(self, match_id):
        logger.info('Sharding replay for {0}'.format(match_id))

        pmses = PlayerMatchSummary.objects.filter(
            match__steam_id=match_id
        ).select_related('hero')
        match = Match.objects.get(steam_id=match_id)

        replay = json.loads(gunzip_str(match.compressed_replay.read()))
        states = [
            x for x in replay if x['type'] == 'state' and x['key'] == 'PLAYING'
        ]
        try:
            offset = states[0]['time']
        except IndexError:
            offset = 0
            logger.warning(
                'Failed to get an offset with match {0}'.format(match_id)
            )

        for pms in pmses:

            hero_msgs = [
                offset_msg(x, offset) for x in replay if filter_msgs(pms, x)
            ]

            buff = BytesIO(gzip_str(json.dumps(hero_msgs)))
            _ = buff.seek(0)  # NOQA
            filename = '{0}_{1}_parse_shard.json.gz'.format(
                match.steam_id,
                pms.player_slot
            )
            pms.replay_shard.save(filename, File(buff))
            pms.set_encoding()

        mr = MatchRequest.objects.get(match_id=match_id)
        mr.raw_parse_url = filename,
        mr.status = MatchRequest.PARSED
        mr.save()


def filter_msgs(pms, msg):
    hero_name = pms.hero.internal_name
    unit = msg.get('unit', None)  # Most messages
    target_source = msg.get('target_source', None)   # Kill/smg
    slot = msg.get('slot', None)   # Buyback

    hero_name_length = len(hero_name)

    if (
        target_source == hero_name
        or unit == hero_name
        or slot == pms.player_slot
    ):
        return True
    else:
        try:
            # Hero Illusions are "{hero_name} (illusion)"
            substring_name = unit[0:hero_name_length]
            if substring_name == hero_name:
                return True
            else:
                return False
        except TypeError:
            return False


def offset_msg(msg, offset):
    msg['offset_time'] = msg['time'] - offset
    return msg
