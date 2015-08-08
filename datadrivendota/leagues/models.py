from django.templatetags.static import static
from django.db import models
from .managers import SortedLeagueManager
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


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

    steam_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, null=True)  # Made up constant
    description = models.CharField(max_length=300, null=True)
    tournament_url = models.CharField(max_length=300, null=True)
    item_def = models.IntegerField(null=True)
    valve_cdn_image = models.TextField(
        null=True, help_text='Steam cdn image url'
    )
    image_ugc = models.BigIntegerField(null=True)  # Through live league games
    tier = models.IntegerField(choices=LEAGUE_TYPES, null=True, blank=True)
    fantasy = models.NullBooleanField(null=True, blank=True)
    update_time = models.DateTimeField(default=timezone.now)

    @property
    def image(self):
        return self.valve_cdn_image or static('blank_league.png')

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
            self.valve_cdn_image is None
            or self.valve_cdn_image == ''
            or self.update_time < (
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
