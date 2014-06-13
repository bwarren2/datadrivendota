from django.db import models
from datadrivendota.utilities import safen


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
    league_id = models.IntegerField()
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
            '1 is normal, 2 is high, 3 is very high, 0 is my not-assigned'
        )
    )
    dire_guild = models.ForeignKey(
        'guilds.Guild',
        null=True,
        related_name='dire_guild'
    )
    radiant_guild = models.ForeignKey(
        'guilds.Guild',
        null=True,
        related_name='radiant_guild'
    )

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
        # @todo: This doesn't currently return a unicode object, but a string
        # object. Bad news bears!
        # --kit 2014-02-16
        return (
            "Match "
            + str(self.match.steam_id)
            + ", User "
            + str(self.player.steam_id)
        )

    def which_side(self):
        """ Returns radiant or dire based on player slot."""
        if self.player_slot < 5:
            return 'Radiant'
        else:
            return 'Dire'

    def derive_attribute(summaries, attribute):
        if attribute == 'duration':
            vector_list = [
                summary.match.duration / 60.0
                for summary in summaries
            ]
        elif attribute == 'K-D+.5*A':
            vector_list = [
                summary.kills - summary.deaths + summary.assists*.5
                for summary in summaries
            ]
        elif attribute == 'player':
            vector_list = [
                summary.player.persona_name
                for summary in summaries
            ]
        elif attribute == 'is_win':
            vector_list = [
                'Won' if summary.is_win else 'Lost'
                for summary in summaries
            ]
        elif attribute == 'game_mode':
            vector_list = [
                summary.match.game_mode.description
                for summary in summaries
            ]
        elif attribute == 'skill':
            vector_list = [summary.match.skill for summary in summaries]
        elif attribute == 'hero_name':
            vector_list = [safen(summary.hero.name) for summary in summaries]
        elif attribute == 'first_blood_time':
            vector_list = [
                summary.match.first_blood_time / 60.0
                for summary in summaries
            ]
        else:
            vector_list = [
                getattr(summary, attribute)
                for summary in summaries
            ]

        label = fetch_attribute_label(attribute)
        return vector_list, label


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


def fetch_match_attributes(summaries, attribute):

    if attribute == 'No Split':
        vector_list = ['No split' for summary in summaries]
        label = 'No Split'
    else:
        vector_list = [
            fetch_pms_attribute(summary, attribute)
            for summary in summaries
        ]

        label = fetch_attribute_label(attribute)
    return vector_list, label


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
        return summary.which_side()
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


def fetch_single_attribute(summary, attribute, compressor='sum'):
    if compressor == 'sum':
        denominator = 1
    else:
        denominator = 5
    if attribute == 'duration':
        return summary.match.duration/60.0/5
    elif attribute == 'K-D+.5*A':
        return (
            (summary.kills - summary.deaths + summary.assists * .5)
            / denominator
        )
    elif attribute == 'is_win':
        return 'Won' if summary.is_win else 'Lost'
    elif attribute == 'game_mode':
        return summary.match.game_mode.description
    elif attribute == 'skill':
        return summary.match.skill
    elif attribute == 'none':
        return ''
    else:
        return getattr(summary, attribute)/denominator


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


def skill_name(skill):
    if skill == 1:
        return 'Normal Skill'
    if skill == 2:
        return 'High Skill'
    if skill == 3:
        return 'Very High Skill'
    else:
        return skill

