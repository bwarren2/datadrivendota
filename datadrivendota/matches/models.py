from datetime import datetime, timedelta
from django.db import models
from utils import safen


class Match(models.Model):

    steam_id = models.IntegerField(help_text="Valve's id field", unique=True)
    match_seq_num = models.IntegerField(help_text="ID valve's play sequence")
    cluster = models.IntegerField()
    start_time = models.IntegerField(help_text='Start time in UTC seconds')
    duration = models.IntegerField()

    radiant_win = models.BooleanField()
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

    replay = models.FileField(upload_to='matches/replays/', null=True)

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

    class Meta:
        verbose_name_plural = 'matches'
        ordering = ['-start_time']

    def __unicode__(self):
        return unicode(self.steam_id)

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
        return self.playermatchsummary_set.\
            filter(player_slot__lt=5).select_related().order_by('player_slot')

    @property
    def dire(self):
        return self.playermatchsummary_set.\
            filter(player_slot__gte=5).select_related().order_by('player_slot')


class GameMode(models.Model):
    steam_id = models.IntegerField(
        help_text="Valve's id field",
        unique=True,
        db_index=True
    )
    description = models.CharField(help_text='Game mode, ie. captains',
                                   max_length=50)
    is_competitive = models.BooleanField(help_text="""Whether charts should
        show this mode by default""", default=False)
    visible = models.BooleanField(default=False)

    class Meta:
        ordering = ['steam_id']

    def __unicode__(self):
        return self.description+', ('+str(self.steam_id)+')'


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
        return self.description+', ('+str(self.steam_id)+')'


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
    gold = models.IntegerField()
    last_hits = models.IntegerField()
    denies = models.IntegerField()
    gold_per_min = models.IntegerField()
    xp_per_min = models.IntegerField()
    gold_spent = models.IntegerField()
    hero_damage = models.IntegerField()
    tower_damage = models.IntegerField()
    hero_healing = models.IntegerField()
    level = models.IntegerField()
    is_win = models.BooleanField()

    class Meta:
        ordering = ['match', 'player_slot']

    def save(self, *args, **kwargs):
        self.is_win = self.determine_win()
        super(PlayerMatchSummary, self).save(*args, **kwargs)

    def determine_win(self):
        """Tells you whether this player was on the winning side of the match.
        5 is a magic number because the left-most bit being set in the returned
        data indicated that the player was dire, the right most bits indicating
        position (0-4)."""

        if self.match.radiant_win is True and self.player_slot < 5:
            return True
        if self.match.radiant_win is False and self.player_slot > 5:
            return True
        return False

    def __unicode__(self):
        return unicode(
            "Match "
            + str(self.match.steam_id)
            + ", User "
            + str(self.player.steam_id)
        )

    @property
    def kda2(self):
        return self.kills - self.deaths + self.assists/2.0

    @property
    def gold_total(self):
        return self.gold_per_min*self.match.duration/60

    @property
    def xp_total(self):
        return self.xp_per_min*self.match.duration/60

    @property
    def improper_player(self):
        return self.leaver.steam_id > 0

    @property
    def side(self):
        """ Returns radiant or dire based on player slot."""
        if self.player_slot < 5:
            return 'Radiant'
        else:
            return 'Dire'

    @property
    def display_date(self):
        return str(
            datetime.fromtimestamp(
                self.match.start_time
            ).strftime('%Y-%m-%d')
        )

    @property
    def display_duration(self):
        return str(
            timedelta(
                seconds=self.match.duration
            )
        )


class AdditionalUnit(models.Model):
    player_match_summary = models.OneToOneField('PlayerMatchSummary')
    unit_name = models.CharField(max_length=50)
    item_0 = models.ForeignKey('items.Item', related_name='additem0')
    item_1 = models.ForeignKey('items.Item', related_name='additem1')
    item_2 = models.ForeignKey('items.Item', related_name='additem2')
    item_3 = models.ForeignKey('items.Item', related_name='additem3')
    item_4 = models.ForeignKey('items.Item', related_name='additem4')
    item_5 = models.ForeignKey('items.Item', related_name='additem5')


class PickBan(models.Model):
    match = models.ForeignKey('Match')
    is_pick = models.BooleanField()
    hero = models.ForeignKey('heroes.Hero')
    team = models.IntegerField()
    order = models.IntegerField()

    class Meta:
        ordering = ['order']


class LeaverStatus(models.Model):
    steam_id = models.IntegerField(unique=True)
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'LeaverStatus'
        verbose_name_plural = 'LeaverStatuses'
        ordering = ['steam_id']

    def __unicode__(self):
        return self.description+', ('+str(self.steam_id)+')'


class SkillBuild(models.Model):
    player_match_summary = models.ForeignKey('PlayerMatchSummary')
    ability = models.ForeignKey('heroes.Ability')
    time = models.IntegerField()
    level = models.IntegerField()

    class Meta:
        ordering = ['player_match_summary', 'level']

    def __unicode__(self):
        return str(self.player_match_summary.id)+', '+str(self.level)
        pass


#############################################
#############################################
#           Deprecations begin here.        #
#############################################
#############################################


# This is used in some JS, the json_data functions.
def skill_name(skill):
    if skill == 1:
        return 'Normal Skill'
    if skill == 2:
        return 'High Skill'
    if skill == 3:
        return 'Very High Skill'
    if skill == 4:
        return 'Tournament Game'
    else:
        return skill


# Everything below here is basically only in the json_data calls.
def fetch_pms_attribute(summary, attribute):
    if attribute == 'duration':
        return summary.match.duration/60.0
    elif attribute == 'K-D+.5*A':
        return summary.kills - summary.deaths + summary.assists * .5
    elif attribute == 'player':
        return summary.player.display_name
    elif attribute == 'is_win':
        return 'Won' if summary.is_win else 'Lost'
    elif attribute == 'game_mode':
        return summary.match.game_mode.description
    elif attribute == 'skill':
        return summary.match.skill
    elif attribute == 'skill_name':
        skill = summary.match.skill
        return skill_name(skill)
    elif attribute == 'hero_name':
        return safen(summary.hero.name)
    elif attribute == 'hero_steam_id':
        return summary.hero.steam_id
    elif attribute == 'first_blood_time':
        return summary.match.first_blood_time/60.0
    elif attribute == 'match_id':
        return summary.match.steam_id
    elif attribute == 'which_side':
        return summary.side
    elif attribute == 'gold_total':
        return summary.gold_per_min*summary.match.duration/60
    elif attribute == 'xp_total':
        return summary.xp_per_min*summary.match.duration/60
    else:
        return getattr(summary, attribute)


def pms_db_args(var, summary=None):
    if var == 'gold_total':
        if summary is None:
            return ['gold_per_min', 'duration']
        else:
            return summary['gold_per_min']*summary['match__duration']/60
    if var == 'xp_total':
        if summary is None:
            return ['xp_per_min', 'duration']
        else:
            return summary['xp_per_min']*summary['match__duration']/60
    if var == 'K-D+.5*A':
        if summary is None:
            return ['kills', 'deaths', 'assists']
        else:
            return summary['kills'] \
                - summary['deaths'] + summary['assists'] * .5
    if var == 'first_blood_time':
        if summary is None:
            return ['match__first_blood_time']
        else:
            return summary['match__first_blood_time']/60.0
    if var == 'player':
        if summary is None:
            return [
                'player',
                'player__steam_id',
                'player__persona_name',
                'player__pro_name'
            ]
        else:
            return summary['player__steam_id']
    if var == 'game_mode':
        if summary is None:
            return ['match__game_mode', 'match__game_mode__description']
        else:
            return summary['match__game_mode__steam_id']
    if var == 'duration':
        if summary is None:
            return ['match__duration']
        else:
            return summary['match__duration']/60.0
    if var == 'match_id':
        if summary is None:
            return ['match__steam_id']
        else:
            return summary['match__steam_id']
    if var == 'hero':
        if summary is None:
            return ['hero__name', 'hero__steam_id']
        else:
            return summary['hero__steam_id']
    if var == 'skill':
        if summary is None:
            return ['match__skill']
        else:
            return summary['match__skill']
    if var == 'None' or var is None:
        if summary is None:
            return []
        else:
            return None

    #Specialized subset calls for a given pms
    if summary is not None:
        if var == 'is_win':
            return 'Won' if summary['is_win'] else 'Lost'
        if var == 'skill_name':
            return skill_name(summary['match__skill'])
        if var == 'hero_name':
            return safen(summary['hero__name'])
        if var == 'hero_steam_id':
            return summary['hero__steam_id']
        if var == 'game_mode_name':
            return summary['match__game_mode__description']
        if var == 'player_display_name':
            if summary['player__pro_name'] is not None:
                return summary['player__pro_name']
            else:
                return summary['player__persona_name']
        return summary.get(var)

    #Summary is none, not one of the special cases.  Just get that attr.
    return [var]




def display_attr(var, summary=None):
    if var == 'player':
        if summary is not None:
            return pms_db_args('player_display_name', summary)
        else:
            return 'Player Name'
    if var == 'is_win':
        if summary is not None:
            return pms_db_args('is_win', summary)
        else:
            return 'Win/Loss'
    if var == 'game_mode':
        if summary is not None:
            return pms_db_args('game_mode_name', summary)
        else:
            return 'Win/Loss'
    if var == 'None' or var is None:
        return None


def fetch_attribute_label(attribute):
    if attribute == 'duration':
        label = 'GameLength(m)'
    elif attribute == 'K-D+.5*A':
        label = 'Kills-Death+.5*Assists'
    elif attribute == 'player':
        label = attribute.title()
    elif attribute == 'is_win':
        label = 'WonGame?'
    elif attribute == 'game_mode':
        label = 'GameMode'
    elif attribute == 'skill':
        label = 'Skill(3=VeryHigh)'
    elif attribute == 'hero_name':
        label = 'HeroName'
    elif attribute == 'first_blood_time':
        label = 'FirstBloodTime(m)'
    elif attribute == 'gold_per_min':
        label = 'Gold Per Min'
    elif attribute == 'xp_per_min':
        label = 'XP Per Min'
    elif attribute == 'none':
        label = ''
    else:
        label = safen(attribute)
    return label
