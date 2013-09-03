from django.db import models

# For the name, internal_name, and valve_id, see:
# https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key=<YOURKEY>&language=en_us


class Hero(models.Model):
    name = models.CharField(max_length=200,
                            help_text="In-game name.")
    machine_name = models.SlugField(max_length=200,
                                    help_text="What goes in URLs.  See slugify()")
    internal_name = models.CharField(max_length=200,
                                     help_text="The protobuf string for the hero")

    steam_id = models.PositiveIntegerField(unique=True, help_text="Valve's int")
    lore = models.TextField(null=True)
    role = models.ManyToManyField('Role')
    mugshot = models.ImageField(null=True, upload_to='heroes/img/',
                                max_length=150)
    thumbshot = models.ImageField(null=True, upload_to='heroes/img/')

    class Meta:
        verbose_name_plural = 'heroes'
        ordering = ['name']
    def __unicode__(self):
        return self.name
    def safe_name(self):
        return safen(self.machine_name)

class Role(models.Model):
    ROLES = (
        ('LaneSupport', 'Lane Support'),
        ('Carry', 'Carry'),
        ('Disabler', 'Disabler'),
        ('Ganker', 'Ganker'),
        ('Nuker', 'Nuker'),
        ('Initiator', 'Initiator'),
        ('Jungler', 'Jungler'),
        ('Pusher', 'Pusher'),
        ('Roamer', 'Roamer'),
        ('Durable', 'Durable'),
        ('Escape', 'Escape'),
        ('Support', 'Support')
    )

    name = models.CharField(max_length=50, choices=ROLES, unique=True)
    desc = models.TextField()

    def __unicode__(self):
        return self.name


class Ability(models.Model):
    steam_id = models.IntegerField(help_text="Valve's internal map", unique=True)
    internal_name = models.CharField(help_text="Valve's underscore name",
                                     max_length=150)

    class Meta:
        verbose_name_plural = 'abilities'

    def __unicode__(self):
        return self.internal_name+' ('+str(self.steam_id)+')'


class HeroDossier(models.Model):
    STAT_ALIGNMENTS = (
        ('strength', 'strength'),
        ('agility', 'agility'),
        ('intelligence', 'intelligence'),
    )
    hero = models.OneToOneField('Hero')
    movespeed = models.IntegerField()
    max_dmg = models.IntegerField()
    min_dmg = models.IntegerField()
    hp = models.IntegerField(help_text="HP after str modification", default=150, editable=False)
    mana = models.IntegerField()
    hp_regen = models.FloatField()
    mana_regen = models.FloatField()
    armor = models.FloatField()
    range = models.IntegerField()
    projectile_speed = models.FloatField()
    strength = models.FloatField()
    agility = models.FloatField()
    intelligence = models.FloatField()
    strength_gain = models.FloatField()
    agility_gain = models.FloatField()
    intelligence_gain = models.FloatField()
    alignment = models.CharField(null=True,
                                 max_length=20, choices=STAT_ALIGNMENTS,
                                 help_text="Str, Int, Agi.")
    base_atk_time = models.FloatField()
    day_vision = models.IntegerField()
    night_vision = models.IntegerField()
    atk_point = models.FloatField()
    atk_backswing = models.FloatField()
    cast_point = models.FloatField()
    cast_backswing = models.FloatField()
    turn_rate = models.FloatField()
    legs = models.IntegerField()

    def __unicode__(self):
        return self.hero.name

def safen(machine_name):
    return machine_name.replace('-',' ').title()
