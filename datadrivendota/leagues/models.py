from datetime import timedelta

from django.templatetags.static import static
from django.db import models
from django.utils import timezone
from django.conf import settings

from .managers import SortedLeagueManager


class League(models.Model):

    """
    A tournament.

    These are game series to which you can buy a ticket in the game client
    """

    AMATEUR = 0
    PRO = 1
    PREMIUM = 2
    LEAGUE_TYPES = (
        (AMATEUR, 'Amateur'),
        (PRO, 'Professional'),
        (PREMIUM, 'Premium'),
    )
    URL_MAP = {
        AMATEUR: 'am',
        PRO: 'pro',
        PREMIUM: 'premium',
    }

    steam_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, null=True)  # Made up constant
    description = models.CharField(max_length=300, null=True)
    tournament_url = models.CharField(max_length=300, null=True)
    item_def = models.IntegerField(null=True)

    tier = models.IntegerField(choices=LEAGUE_TYPES, null=True, blank=True)
    fantasy = models.NullBooleanField(null=True, blank=True)
    update_time = models.DateTimeField(default=timezone.now)

    stored_image = models.ImageField(null=True, upload_to='leagues/img/')
    image_failed = models.BooleanField(default=False)
    image_ugc = models.BigIntegerField(null=True)  # Through live league games

    @property
    def image(self):
        if self.image_failed is True:
            return static('blanks/blank_league.png')
        else:
            try:
                return self.stored_image.url
            except ValueError:
                return static('blanks/blank_league.png')

    @property
    def tier_name(self):
        try:
            return dict(self.LEAGUE_TYPES)[self.tier]
        except ValueError:
            return None

    @property
    def display_name(self):
        if self.name is not None:
            str = self.name.replace('#DOTA_Item_League_', '')
            str = str.replace('#DOTA_Item_', '').replace('_', ' ')
            return str
        else:
            return ''

    @property
    def display_description(self):
        if self.description is not None:
            str = self.description.replace('#DOTA_Item_League_', '')
            str = str.replace('#DOTA_Item_Desc_', '').replace('_', ' ')
            str = str.replace('#DOTA_Item_', '').replace('_', ' ')
            return str
        else:
            return ''

    def __unicode__(self):
        if self.name is None:
            return 'League #{0}'.format(self.steam_id)
        else:
            return self.name

    @property
    def is_outdated(self):
        if (
            self.image == static('blanks/blank_league.png') and
            self.update_time < (
                timezone.now() - timedelta(
                    seconds=settings.UPDATE_LAG_UTC
                )
            )
        ):
            return True
        else:
            return False

    objects = models.Manager()
    recency = SortedLeagueManager()

    def save(self, *args, **kwargs):
        self.update_time = timezone.now()
        super(League, self).save(*args, **kwargs)


class ScheduledMatch(models.Model):
    league = models.ForeignKey('leagues.League')
    game_id = models.IntegerField()
    team_1 = models.ForeignKey(
        'teams.Team',
        related_name='scheduled_team_1_set',
        null=True
    )
    team_2 = models.ForeignKey(
        'teams.Team',
        related_name='scheduled_team_2_set',
        null=True
    )
    start_time = models.IntegerField(help_text='Start time in UTC seconds')
    comment = models.TextField()
    final = models.BooleanField()

    class Meta:
        unique_together = (
            'league', 'game_id', 'team_1', 'team_2', 'start_time'
        )


class LiveMatch(models.Model):
    league_id = models.PositiveIntegerField()
    steam_id = models.BigIntegerField(unique=True)
    radiant_team = models.PositiveIntegerField(null=True, blank=True)
    dire_team = models.PositiveIntegerField(null=True, blank=True)
    radiant_logo_ugc = models.BigIntegerField(null=True, blank=True)
    dire_logo_ugc = models.BigIntegerField(null=True, blank=True)
    failed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def ready(self):
        return self.created_at < timezone.now() - timedelta(
            minutes=settings.LIVE_MATCH_LOOKBACK_MINUTES,
        )

    @property
    def expired(self):
        return self.created_at < timezone.now() - timedelta(
            days=settings.FAILED_LIVEMATCH_KEEP_DAYS
        )

    class Meta:
        unique_together = (
            'league_id', 'steam_id', 'radiant_team', 'dire_team'
        )
