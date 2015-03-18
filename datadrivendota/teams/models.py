from django.db import models
from .managers import SortedTeamManager, TI4TeamManager
from django.utils import timezone


class Team(models.Model):
    """Pro team data"""
    steam_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, null=True)
    tag = models.CharField(max_length=200, null=True)
    created = models.IntegerField(null=True)
    rating = models.CharField(max_length=50, null=True)
    logo = models.BigIntegerField(null=True)
    logo_sponsor = models.BigIntegerField(null=True)
    country_code = models.CharField(max_length=10, null=True)
    url = models.CharField(max_length=200, null=True)
    games_played_with_current_roster = models.IntegerField(null=True)
    player_0 = models.ForeignKey(
        'players.Player', related_name='player_0', null=True
        )
    player_1 = models.ForeignKey(
        'players.Player', related_name='player_1', null=True
        )
    player_2 = models.ForeignKey(
        'players.Player', related_name='player_2', null=True
        )
    player_3 = models.ForeignKey(
        'players.Player', related_name='player_3', null=True
        )
    player_4 = models.ForeignKey(
        'players.Player', related_name='player_4', null=True
        )
    admin = models.ForeignKey(
        'players.Player', related_name='team_admin', null=True
        )
    leagues = models.ManyToManyField('leagues.League')
    valve_cdn_image = models.TextField(
        null=True, help_text='Steam cdn image url'
    )
    valve_cdn_sponsor_image = models.TextField(
        null=True, help_text='Steam cdn sponsor image url'
    )
    update_time = models.DateTimeField(default=timezone.now)

    objects = models.Manager()
    sorted = SortedTeamManager()
    TI4 = TI4TeamManager()

    @property
    def image(self):
        if self.valve_cdn_sponsor_image is not None:
            return self.valve_cdn_sponsor_image
        else:
            return (
                'https://s3.amazonaws.com/datadrivendota/'
                'blanks/blank_team.png'
                )

    def save(self, *args, **kwargs):
        self.update_time = timezone.now()
        super(Team, self).save(*args, **kwargs)


def assemble_pros(teams):
    lst = []
    subset = teams.exclude(player_0=None).values('player_0__steam_id')
    addition = [t['player_0__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(player_1=None).values('player_1__steam_id')
    addition = [t['player_1__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(player_2=None).values('player_2__steam_id')
    addition = [t['player_2__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(player_3=None).values('player_3__steam_id')
    addition = [t['player_3__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(player_4=None).values('player_4__steam_id')
    addition = [t['player_4__steam_id'] for t in subset]
    lst.extend(addition)

    subset = teams.exclude(admin=None).values('admin__steam_id')
    addition = [t['admin__steam_id'] for t in subset]
    lst.extend(addition)
    return lst
