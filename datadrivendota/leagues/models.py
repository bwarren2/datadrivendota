from django.db import models
from .managers import SortedLeagueManager
from django.utils import timezone


class League(models.Model):
    """Analogous to a tournament, these are game series to which you can buy a ticket in the game client"""
    steam_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, null=True)  # Made up constant
    description = models.CharField(max_length=300, null=True)  # Made up constant
    tournament_url = models.CharField(max_length=300, null=True)
    item_def = models.IntegerField(null=True)
    logo_image = models.ImageField(
        upload_to='leagues/img/', null=True, default='blank_team.png'
    )
    valve_cdn_image = models.TextField(
        null=True, help_text='Steam cdn image url'
    )
    update_time = models.DateTimeField(default=timezone.now)

    @property
    def display_name(self):
        str = self.name.replace('#DOTA_Item_League_', '')
        str = str.replace('#DOTA_Item_', '').replace('_', ' ')
        return str

    @property
    def display_description(self):
        str = self.description.replace('#DOTA_Item_League_', '')
        str = str.replace('#DOTA_Item_Desc_', '').replace('_', ' ')
        str = str.replace('#DOTA_Item_', '').replace('_', ' ')
        return str

    def __unicode__(self):
        if self.name is None:
            return 'League #{0}'.format(self.steam_id)
        else:
            return self.name

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
