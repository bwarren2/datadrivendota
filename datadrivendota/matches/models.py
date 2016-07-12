from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.utils import timezone
import time

from .querysets import (
    PMSQuerySet,
    MatchFilteredQuerySet,
    FilteredQuerySet,
)
from .managers import (
    Unparsed,
    Parsed,
    ParsedPMS,
    UnparsedPMS,
)
from .model_fields import ReplayFragmentField


class Match(models.Model):

    # Magic numbers given by Valve
    PLAYER_SLOTS = [0, 1, 2, 3, 4, 128, 129, 130, 131, 132]
    RADIANT_SLOTS = [0, 1, 2, 3, 4]
    DIRE_SLOTS = [128, 129, 130, 131, 132]

    steam_id = models.BigIntegerField(
        help_text="Valve's id field", unique=True
    )
    match_seq_num = models.BigIntegerField(
        help_text="ID valve's play sequence",
        null=True,
        blank=True
    )
    cluster = models.IntegerField()
    start_time = models.IntegerField(help_text='Start time in UTC seconds')
    duration = models.IntegerField()

    radiant_win = models.NullBooleanField()
    tower_status_radiant = models.IntegerField()
    tower_status_dire = models.IntegerField()
    barracks_status_radiant = models.IntegerField()
    barracks_status_dire = models.IntegerField()

    first_blood_time = models.IntegerField()
    human_players = models.IntegerField()
    league = models.ForeignKey('leagues.League', null=True)
    positive_votes = models.IntegerField()
    negative_votes = models.IntegerField()
    lobby_type = models.ForeignKey(
        'LobbyType',
        help_text='How the game was queued'
    )
    game_mode = models.ForeignKey('GameMode')
    skill = models.IntegerField(
        default=0,
        help_text=(
            'How valve denotes skill bracket.  '
            '1 is normal, 2 is high, 3 is very high, '
            '0 is my not-assigned, 4 is Tournament'
        )
    )
    radiant_guild = models.ForeignKey(
        'guilds.Guild',
        null=True,
        related_name='radiant_guild'
    )
    dire_guild = models.ForeignKey(
        'guilds.Guild',
        null=True,
        related_name='dire_guild'
    )

    radiant_team = models.ForeignKey(
        'teams.Team',
        null=True,
        related_name='radiant_team'
    )
    radiant_team_complete = models.NullBooleanField()
    dire_team = models.ForeignKey(
        'teams.Team',
        null=True,
        related_name='dire_team'
    )
    dire_team_complete = models.NullBooleanField()

    series_id = models.IntegerField(null=True)
    series_type = models.IntegerField(null=True)

    replay = models.FileField(
        upload_to='matches/replays/',
        null=True,
        blank=True,
    )
    compressed_replay = models.FileField(
        upload_to='matches/replays/',
        null=True,
        blank=True,
    )

    parsed_with = models.CharField(
        max_length=50, null=True, blank=True, default=None
    )
    replay_salt = models.CharField(max_length=30, null=True, blank=True)

    UNPROCESSED = 0
    LEGIT = 1
    UNCOUNTED = 2

    VALIDITY_CHOICES = (
        (UNPROCESSED, 'Unprocessed'),
        (LEGIT, 'Legitimate'),
        (UNCOUNTED, 'Abandoned'),
    )
    validity = models.IntegerField(
        choices=VALIDITY_CHOICES,
        default=UNPROCESSED
    )

    objects = FilteredQuerySet.as_manager()
    unparsed = Unparsed()
    parsed = Parsed()

    class Meta:
        verbose_name_plural = 'matches'
        ordering = ['-start_time']

    def __unicode__(self):
        return unicode(self.steam_id)

    @property
    def replay_url(self):
        """ Uniqueness prefix from the parsed output hash function. """
        if (
            self.cluster is None
            or self.steam_id  is None
            or self.replay_salt is None
        ):
            return None
        else:
            return "http://replay{0}.valve.net/570/{1}_{2}.dem.bz2".format(
                self.cluster, self.steam_id, self.replay_salt
            )

    @property
    def is_parsed(self):
        return self.parsed_with == settings.PARSER_VERSION

    @property
    def is_too_old(self):
        " Can we expect still valve to have the replay for parsing? "
        now = timezone.now()
        one_week_ago = now - timedelta(weeks=1)
        one_week_ago = time.mktime(one_week_ago.timetuple())

        return self.start_time < one_week_ago

    @property
    def is_too_new(self):
        " Can we expect valve to have the replay for parsing yet? "
        now = timezone.now()
        ten_min_ago = now - timedelta(minutes=10)
        ten_min_ago = time.mktime(ten_min_ago.timetuple())
        return self.start_time > ten_min_ago

    @property
    def is_parsable(self):

        return not self.is_too_new and not self.is_too_old

    @cached_property
    def parse_status(self):
        from parserpipe.models import MatchRequest
        has_completed_match_request = MatchRequest.objects.filter(
            match_id=self.steam_id,
            status=MatchRequest.COMPLETE,
        ).first()
        if has_completed_match_request:
            return MatchRequest.STATUS_CHOICES[MatchRequest.COMPLETE]
        highest_status = MatchRequest.objects.filter(
            match_id=self.steam_id,
        ).order_by(
            '-status',
        ).values_list(
            'status',
            flat=True,
        ).first()
        if not highest_status:
            return 'unrequested'
        return dict(MatchRequest.STATUS_CHOICES)[highest_status]

    @property
    def hms_duration(self):
        return timedelta(seconds=self.duration)

    @property
    def hms_start_time(self):
        return datetime.fromtimestamp(
            self.start_time
        ).strftime('%H:%M:%S %Y-%m-%d')

    @property
    def radiant(self):
        # These cause new querysets; be careful
        return self.playermatchsummary_set.filter(
            player_slot__lt=5
        ).order_by('player_slot')

    @property
    def dire(self):
        # These cause new querysets; be careful
        return self.playermatchsummary_set.filter(
            player_slot__gte=5
        ).order_by('player_slot')


class GameMode(models.Model):
    steam_id = models.IntegerField(
        help_text="Valve's id field",
        unique=True,
        db_index=True
    )
    description = models.CharField(help_text='Game mode, ie. captains',
                                   max_length=50)
    is_competitive = models.BooleanField(
        help_text="""Whether charts should
        show this mode by default""",
        default=False
    )
    visible = models.BooleanField(default=False)

    class Meta:
        ordering = ['steam_id']

    def __unicode__(self):
        return u"{0}, ({1})".format(self.description, self.steam_id)

    @property
    def has_bans(self):
        # Magic numbers per valve's def of capt, reverse capt
        return self.steam_id in [2, 8]


class LobbyType(models.Model):
    steam_id = models.IntegerField(
        help_text='How the queue occurred',
        unique=True
    )
    description = models.CharField(help_text='Queue type', max_length=50)

    class Meta:
        verbose_name = 'LobbyType'
        verbose_name_plural = 'LobbyTypes'
        ordering = ['steam_id']

    def __unicode__(self):
        return u"{0}, ({1})".format(self.description, self.steam_id)


class PlayerMatchSummary(models.Model):
    match = models.ForeignKey('Match')
    player = models.ForeignKey('players.Player')
    hero = models.ForeignKey('heroes.Hero')
    player_slot = models.IntegerField()
    leaver = models.ForeignKey('LeaverStatus')
    item_0 = models.ForeignKey('items.Item', related_name='item0')
    item_1 = models.ForeignKey('items.Item', related_name='item1')
    item_2 = models.ForeignKey('items.Item', related_name='item2')
    item_3 = models.ForeignKey('items.Item', related_name='item3')
    item_4 = models.ForeignKey('items.Item', related_name='item4')
    item_5 = models.ForeignKey('items.Item', related_name='item5')
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    gold = models.IntegerField(null=True)
    last_hits = models.IntegerField()
    denies = models.IntegerField()
    gold_per_min = models.IntegerField()
    xp_per_min = models.IntegerField()
    gold_spent = models.IntegerField(null=True)
    hero_damage = models.IntegerField(null=True)
    tower_damage = models.IntegerField()
    hero_healing = models.IntegerField()
    level = models.IntegerField()
    is_win = models.BooleanField()

    # Scheduled for deprecation 1-1-2016
    replay_shard = models.FileField(
        upload_to='playermatchsummaries/replays/',
        null=True,
        blank=True,
    )

    all_data = ReplayFragmentField(max_length=250)

    objects = PMSQuerySet.as_manager()
    unparsed = UnparsedPMS()
    parsed = ParsedPMS()

    class Meta:
        ordering = ['match', 'player_slot']
        unique_together = ("match", "player_slot")

    def save(self, *args, **kwargs):
        self.is_win = self.determine_win()
        super(PlayerMatchSummary, self).save(*args, **kwargs)

    def determine_win(self):
        """
        Determine win-ness.

        Tell you whether this player was on the winning side of the match.
        5 is a magic number because the left-most bit being set in the returned
        data indicated that the player was dire, the right most bits indicating
        position (0-4).
        """
        if self.match.radiant_win is True and self.player_slot < 5:
            return True
        if self.match.radiant_win is False and self.player_slot > 5:
            return True
        return False

    def __unicode__(self):
        return u'Match: {0}, User {1}'.format(
            self.match.steam_id, self.player.steam_id
        )

    @property
    def lookup_pair(self):
        """ Uniqueness prefix from the parsed output hash function. """
        return "{0}_{1}".format(self.match.steam_id, self.player_slot)

    @property
    def kda2(self):
        return self.kills - self.deaths + self.assists / 2.0

    @property
    def gold_total(self):
        return self.gold_per_min * self.match.duration / 60

    @property
    def xp_total(self):
        return self.xp_per_min * self.match.duration / 60

    @property
    def improper_player(self):
        return self.leaver.steam_id > 0

    @property
    def side(self):
        """ Return radiant or dire based on player slot."""
        if self.player_slot < 5:
            return 'Radiant'
        else:
            return 'Dire'

    @property
    def slot_sequence(self):
        if self.side == 'Radiant':
            return self.player_slot

        elif self.side == 'Dire':
            return self.player_slot - 123
            # Dire slots start at 128, but we want to return 5-9

        else:
            raise ValueError(
                'What kind of side is {0} for pms {1}'.format(
                    self.side, self.id
                )
            )

    @property
    def is_radiant(self):
        return self.side == 'Radiant'

    @property
    def is_dire(self):
        return self.side == 'Dire'

    @property
    def display_date(self):
        return datetime.fromtimestamp(
            self.match.start_time
        ).strftime('%Y-%m-%d')

    @property
    def display_duration(self):
        return timedelta(
            seconds=self.match.duration
        )

    @property
    def enemies(self):
        if self.side == 'Radiant':
            return sorted([
                pms.hero.internal_name
                for pms in PlayerMatchSummary.objects.filter(
                    match__steam_id=self.match.steam_id,
                    player_slot__gte=6
                )
            ])
        elif self.side == 'Dire':
            return sorted([
                pms.hero.internal_name
                for pms in PlayerMatchSummary.objects.filter(
                    match__steam_id=self.match.steam_id,
                    player_slot__lte=6
                )
            ])

    @property
    def allies(self):
        if self.side == 'Radiant':
            return sorted([
                pms.hero.internal_name
                for pms in PlayerMatchSummary.objects.filter(
                    match__steam_id=self.match.steam_id,
                    player_slot__lte=6
                )
            ])
        elif self.side == 'Dire':
            return sorted([
                pms.hero.internal_name
                for pms in PlayerMatchSummary.objects.filter(
                    match__steam_id=self.match.steam_id,
                    player_slot__gte=6
                )
            ])

    @property
    def css_classes(self):
        return self.side.lower()


class AdditionalUnit(models.Model):
    player_match_summary = models.OneToOneField('PlayerMatchSummary')
    unit_name = models.CharField(max_length=50)
    item_0 = models.ForeignKey('items.Item', related_name='additem0')
    item_1 = models.ForeignKey('items.Item', related_name='additem1')
    item_2 = models.ForeignKey('items.Item', related_name='additem2')
    item_3 = models.ForeignKey('items.Item', related_name='additem3')
    item_4 = models.ForeignKey('items.Item', related_name='additem4')
    item_5 = models.ForeignKey('items.Item', related_name='additem5')

    class Meta:
        unique_together = ("player_match_summary", "unit_name")


class PickBan(models.Model):
    match = models.ForeignKey('Match')
    is_pick = models.BooleanField()
    hero = models.ForeignKey('heroes.Hero')
    team = models.IntegerField()  # 0 is radiant, 1 is dire
    order = models.IntegerField()

    objects = MatchFilteredQuerySet.as_manager()

    class Meta:
        ordering = ['match', 'order']
        unique_together = ("match", "order")


class LeaverStatus(models.Model):
    steam_id = models.IntegerField(unique=True)
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'LeaverStatus'
        verbose_name_plural = 'LeaverStatuses'
        ordering = ['steam_id']

    def __unicode__(self):
        return u"{0}, ({1})".format(self.description, self.steam_id)


class SkillBuild(models.Model):
    player_match_summary = models.ForeignKey('PlayerMatchSummary')
    level = models.IntegerField()
    ability = models.ForeignKey('heroes.Ability')
    time = models.IntegerField()

    class Meta:
        ordering = ['player_match_summary', 'level']
        unique_together = ("player_match_summary", "level")

    def __unicode__(self):
        return u"{0}, ({1})".format(
            self.player_match_summary.id,
            self.level
        )
