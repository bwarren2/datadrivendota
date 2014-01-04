from django.db import models


# Create your models here.
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
    lobby_type = models.ForeignKey('LobbyType', help_text='How the game was queued')
    game_mode = models.ForeignKey('GameMode')
    skill=models.IntegerField(default=0,
        help_text='How valve denotes skill bracket.  1 is normal, 2 is high, 3 is very high, 0 is my not-assigned')

    UNPROCESSED = 0
    LEGIT = 1
    UNCOUNTED = 2

    VALIDITY_CHOICES = (
        (UNPROCESSED,'Unprocessed'),
        (LEGIT,'Legitimate'),
        (UNCOUNTED,'Abandoned'),
        )
    validity = models.IntegerField(choices=VALIDITY_CHOICES, default=UNPROCESSED)

    class Meta:
        verbose_name_plural = 'matches'
        ordering = ['-start_time']

    def __unicode__(self):
        return unicode(self.steam_id)


class GameMode(models.Model):
    steam_id = models.IntegerField(help_text="Valve's id field", unique=True, db_index=True)
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

    steam_id = models.IntegerField(help_text='How the queue occurred', unique=True)
    description = models.CharField(help_text='Queue type', max_length=50)


    class Meta:
        verbose_name = 'LobbyType'
        verbose_name_plural = 'LobbyTypes'
        ordering=['steam_id']

    def __unicode__(self):
        return self.description+', ('+str(self.steam_id)+')'


class PlayerMatchSummary(models.Model):
    match = models.ForeignKey('Match')
    player = models.ForeignKey('players.Player')
    hero = models.ForeignKey('heroes.Hero')
    player_slot = models.IntegerField()
    leaver = models.ForeignKey('LeaverStatus')
    item_0 = models.IntegerField()
    item_1 = models.IntegerField()
    item_2 = models.IntegerField()
    item_3 = models.IntegerField()
    item_4 = models.IntegerField()
    item_5 = models.IntegerField()
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
        return "Match "+str(self.match.steam_id)+", User "+str(self.player.steam_id)

    def which_side(self):
        """ Returns radiant or dire based on player slot."""
        if self.player_slot < 5:
            return 'Radiant'
        else:
            return 'Dire'

    def derive_attribute(summaries,attribute):
        if attribute=='duration':
            vector_list = [summary.match.duration/60.0 for summary in summaries]
        elif attribute=='K-D+.5*A':
            vector_list = [summary.kills - summary.deaths + summary.assists*.5 for summary in summaries]
        elif attribute == 'player':
            vector_list = [summary.player.persona_name for summary in summaries]
        elif attribute == 'is_win':
            vector_list = ['Won' if summary.is_win==True else 'Lost' for summary in summaries]
        elif attribute == 'game_mode':
            vector_list = [summary.match.game_mode.description for summary in summaries]
        elif attribute == 'skill':
            vector_list = [summary.match.skill for summary in summaries]
        elif attribute == 'hero_name':
            vector_list = [safen(summary.hero.name) for summary in summaries]
        elif attribute == 'first_blood_time':
            vector_list = [summary.match.first_blood_time/60.0 for summary in summaries]
        else:
            vector_list = [getattr(summary, attribute) for summary in summaries]

        label = fetch_attribute_label(attribute)
        return vector_list, label


class LeaverStatus(models.Model):
    steam_id = models.IntegerField(unique=True)
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'LeaverStatus'
        verbose_name_plural = 'LeaverStatuses'
        ordering=['steam_id']
    def __unicode__(self):
        return self.description+', ('+str(self.steam_id)+')'


class SkillBuild(models.Model):
    player_match_summary = models.ForeignKey('PlayerMatchSummary')
    ability = models.ForeignKey('heroes.Ability')
    time = models.IntegerField()
    level = models.IntegerField()

    def __unicode__(self):
        return str(self.player_match_summary.id)+', '+str(self.level)
        pass
