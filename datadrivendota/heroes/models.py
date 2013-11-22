from django.db import models
from django.utils.text import slugify
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
    mugshot = models.ImageField(null=True, upload_to='heroes/img/')
    thumbshot = models.ImageField(null=True, upload_to='heroes/img/')
    visible = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'heroes'
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def safe_name(self):
        return safen(self.machine_name)

    def save(self, *args, **kwargs):
        self.machine_name = slugify(unicode(self.name))
        super(Hero, self).save(*args, **kwargs)


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
    #Things that come from VPK files
    steam_id = models.IntegerField(help_text="Valve's internal map", unique=True)
    internal_name = models.CharField(help_text="Valve's underscore name",max_length=150)
    machine_name = models.CharField(help_text="Valve's underscore name",max_length=150)
    channel_time = models.CharField(help_text="Spaced channel time by level",max_length=150, blank=True)
    damage = models.CharField(help_text="Spaced damage by level",max_length=150, blank=True)
    damage_type = models.CharField(help_text="Damage type",max_length=150, blank=True)
    cast_range = models.CharField(help_text="Spaced cast range by level",max_length=150, blank=True)
    mana_cost = models.CharField(help_text="Spaced mana cost by level",max_length=150, blank=True)
    cast_point = models.CharField(help_text="Spaced cast point by level",max_length=150, blank=True)
    cooldown = models.CharField(help_text="Spaced cooldown by level",max_length=150, blank=True)
    duration = models.CharField(help_text="Spaced duration by level",max_length=150, blank=True)
    is_ultimate  = models.BooleanField(help_text="Is this an ultimate?", blank=True)
    behavior = models.ManyToManyField('AbilityBehavior')
    target_flags = models.ManyToManyField('AbilityUnitTargetFlags')
    target_type = models.ManyToManyField('AbilityUnitTargetType')
    target_team = models.ManyToManyField('AbilityUnitTargetTeam')

    #Things that come from the jsfeed http://www.dota2.com/jsfeed/abilitydata
    name = models.TextField(help_text="Valve's underscore name")
    description = models.TextField(help_text="Tooltip", blank=True)
    notes = models.TextField(help_text="Errata",blank=True)
    lore = models.TextField(help_text="Flavor text",blank=True)
    hero = models.ForeignKey('Hero', null=True)
    picture = models.ImageField(upload_to='heroes/img/', blank=True)
    is_core = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = 'abilities'

    def __unicode__(self):
        return self.internal_name+' ('+str(self.steam_id)+')'

    def save(self, *args, **kwargs):
        self.machine_name = slugify(self.name)
        super(Ability, self).save(*args, **kwargs)


class AbilitySpecialValues(models.Model):
    ability = models.ForeignKey('Ability')
    key = models.CharField(help_text="Valve's underscore name",max_length=150)
    value = models.CharField(help_text="Valve's underscore name",max_length=150)

    def __unicode__(self):
        return ' ('+str(self.key)+': '+self.value+')'


class AbilityBehavior(models.Model):
    internal_name = models.CharField(help_text="Valve's all-caps underscore name",max_length=150)

    def __unicode__(self):
        return human_name(self.internal_name)


class AbilityUnitTargetFlags(models.Model):
    internal_name = models.CharField(help_text="Valve's all-caps underscore name",max_length=150)

    def __unicode__(self):
        return human_name(self.internal_name)


class AbilityUnitTargetType(models.Model):
    internal_name = models.CharField(help_text="Valve's all-caps underscore name",max_length=150)

    def __unicode__(self):
        return human_name(self.internal_name)


class AbilityUnitTargetTeam(models.Model):
    internal_name = models.CharField(help_text="Valve's all-caps underscore name",max_length=150)

    def __unicode__(self):
        return human_name(self.internal_name)


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

def safen(str):
    return str.replace('-',' ').replace('_',' ').title()

def human_name(str):
    return str.replace("_"," ").title()
