from django.templatetags.static import static
from django.db import models
from .managers import SortedTeamManager, TI4TeamManager
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Team(models.Model):

    """ Pro team data. """

    steam_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, null=True)
    tag = models.CharField(max_length=200, null=True)
    created = models.IntegerField(null=True)
    rating = models.CharField(max_length=50, null=True)
    logo = models.BigIntegerField(null=True)
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
    image_ugc = models.BigIntegerField(null=True)  # Through live league games
    stored_image = models.ImageField(null=True, upload_to='teams/img/')
    update_time = models.DateTimeField(default=timezone.now)

    objects = models.Manager()
    sorted = SortedTeamManager()
    TI4 = TI4TeamManager()

    @property
    def image(self):
        try:
            return self.stored_image.url
        except ValueError:
            return static('blank_team.png')

    @property
    def is_outdated(self):
        if (
            self.image == static('blank_team.png')
            and self.update_time < (
                timezone.now() - timedelta(
                    seconds=settings.UPDATE_LAG_UTC
                )
            )
        ):
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        self.update_time = timezone.now()
        super(Team, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


def assemble_pros(teams):
    """ Filter out players on teams. """
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
