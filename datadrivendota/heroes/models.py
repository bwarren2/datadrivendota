from django.db import models
from django.utils.text import slugify
from .managers import VisibleHeroManager
# For the name, internal_name, and valve_id, see:
# https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/
#       ?key=<YOURKEY>&language=en_us


class Role(models.Model):
    LANESUPPORT = 'LaneSupport'
    CARRY = 'Carry'
    DISABLER = 'Disabler'
    GANKER = 'Ganker'
    NUKER = 'Nuker'
    INITIATOR = 'Initiator'
    JUNGLER = 'Jungler'
    PUSHER = 'Pusher'
    ROAMER = 'Roamer'
    DURABLE = 'Durable'
    ESCAPE = 'Escape'
    SUPPORT = 'Support'
    ROLES = (
        (LANESUPPORT, 'Lane Support'),
        (CARRY, 'Carry'),
        (DISABLER, 'Disabler'),
        (GANKER, 'Ganker'),
        (NUKER, 'Nuker'),
        (INITIATOR, 'Initiator'),
        (JUNGLER, 'Jungler'),
        (PUSHER, 'Pusher'),
        (ROAMER, 'Roamer'),
        (DURABLE, 'Durable'),
        (ESCAPE, 'Escape'),
        (SUPPORT, 'Support')
    )
    name = models.CharField(max_length=50, choices=ROLES, unique=True)
    machine_name = models.CharField(max_length=50)
    desc = models.TextField()
    thumbshot = models.ImageField(null=True, upload_to='heroes/img/')

    @property
    def url(self):
        return "images/pips/{}.png".format(self.name.lower())

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.machine_name = slugify(self.name)
        super(Role, self).save(*args, **kwargs)


class Hero(models.Model):
    name = models.CharField(
        max_length=200,
        help_text="In-game name."
    )
    machine_name = models.SlugField(
        max_length=200,
        help_text="What goes in URLs.  See slugify()",
        unique=True,
        null=True
    )
    internal_name = models.CharField(
        max_length=200,
        help_text="The protobuf string for the hero"
    )

    steam_id = models.PositiveIntegerField(
        unique=True,
        help_text="Valve's int"
    )
    lore = models.TextField(null=True)
    mugshot = models.ImageField(null=True, upload_to='heroes/img/')
    thumbshot = models.ImageField(null=True, upload_to='heroes/img/')
    visible = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, through='Assignment')

    objects = models.Manager()
    public = VisibleHeroManager()

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


class Assignment(models.Model):
    hero = models.ForeignKey('Hero')
    role = models.ForeignKey('Role')
    magnitude = models.IntegerField()


class Ability(models.Model):
    #Things that come from VPK files
    steam_id = models.IntegerField(
        help_text="Valve's internal map",
        unique=True
    )
    internal_name = models.CharField(
        help_text="Valve's underscore name",
        max_length=150
    )
    machine_name = models.CharField(
        help_text="Valve's underscore name",
        max_length=150,
        unique=True
    )
    channel_time = models.CharField(
        help_text="Spaced channel time by level",
        max_length=150,
        blank=True
    )
    damage = models.CharField(
        help_text="Spaced damage by level",
        max_length=150,
        blank=True
    )
    damage_type = models.CharField(
        help_text="Damage type",
        max_length=150,
        blank=True
    )
    cast_range = models.CharField(
        help_text="Spaced cast range by level",
        max_length=150,
        blank=True
    )
    mana_cost = models.CharField(
        help_text="Spaced mana cost by level",
        max_length=150,
        blank=True
    )
    cast_point = models.CharField(
        help_text="Spaced cast point by level",
        max_length=150,
        blank=True
    )
    cooldown = models.CharField(
        help_text="Spaced cooldown by level",
        max_length=150,
        blank=True
    )
    duration = models.CharField(
        help_text="Spaced duration by level",
        max_length=150,
        blank=True
    )
    is_ultimate = models.BooleanField(
        help_text="Is this an ultimate?",
        blank=True,
        default=False
    )
    behavior = models.ManyToManyField('AbilityBehavior')
    target_flags = models.ManyToManyField('AbilityUnitTargetFlags')
    target_type = models.ManyToManyField('AbilityUnitTargetType')
    target_team = models.ManyToManyField('AbilityUnitTargetTeam')

    #Things that come from the jsfeed http://www.dota2.com/jsfeed/abilitydata
    name = models.TextField(help_text="Valve's underscore name")
    description = models.TextField(help_text="Tooltip", blank=True)
    notes = models.TextField(help_text="Errata", blank=True)
    lore = models.TextField(help_text="Flavor text", blank=True)
    hero = models.ForeignKey('Hero', null=True)
    picture = models.ImageField(upload_to='heroes/img/', blank=True)
    is_core = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'abilities'

    def __unicode__(self):
        return self.internal_name+' ('+str(self.steam_id)+')'

    def save(self, *args, **kwargs):
        self.machine_name = slugify(self.internal_name)
        super(Ability, self).save(*args, **kwargs)

    def display_damage_type(self):
        return self.damage_type.replace('DAMAGE_TYPE_', '').title()


class AbilitySpecialValues(models.Model):
    ability = models.ForeignKey('Ability')
    key = models.CharField(
        help_text="Valve's underscore name",
        max_length=150
    )
    value = models.CharField(
        help_text="Valve's underscore name",
        max_length=150
    )

    def display_key(self):
        return self.key.replace('_', ' ').title()

    def __unicode__(self):
        return ' ('+str(self.key)+': '+self.value+')'


class AbilityBehavior(models.Model):
    internal_name = models.CharField(
        help_text="Valve's all-caps underscore name",
        max_length=150
    )

    def __unicode__(self):
        return human_name(self.internal_name)

    def display_name(self):
        return self.internal_name.replace(
            'DOTA_ABILITY_BEHAVIOR_', ''
            ).replace('_', ' ').title()


class AbilityUnitTargetFlags(models.Model):
    internal_name = models.CharField(
        help_text="Valve's all-caps underscore name",
        max_length=150
    )

    def display_name(self):
        return self.internal_name.replace(
            'DOTA_UNIT_TARGET_FLAG_', ''
            ).replace('_', ' ').title()

    def __unicode__(self):
        return human_name(self.internal_name)


class AbilityUnitTargetType(models.Model):
    internal_name = models.CharField(
        help_text="Valve's all-caps underscore name",
        max_length=150
    )

    def display_name(self):
        return self.internal_name.replace(
            'DOTA_UNIT_TARGET_', ''
            ).replace('_', ' ').title()

    def __unicode__(self):
        return human_name(self.internal_name)


class AbilityUnitTargetTeam(models.Model):
    internal_name = models.CharField(
        help_text="Valve's all-caps underscore name",
        max_length=150
    )

    def display_name(self):
        return self.internal_name.replace(
            'DOTA_UNIT_TARGET_TEAM_', ''
            ).replace('_', ' ').title()

    def __unicode__(self):
        return human_name(self.internal_name)


class HeroDossier(models.Model):
    STRENGTH = 'strength'
    AGILITY = 'agility'
    INTELLIGENCE = 'intelligence'

    STAT_ALIGNMENTS = (
        (STRENGTH, 'strength'),
        (AGILITY, 'agility'),
        (INTELLIGENCE, 'intelligence'),
    )
    hero = models.OneToOneField('Hero')
    movespeed = models.IntegerField()
    max_dmg = models.IntegerField()
    min_dmg = models.IntegerField()
    hp = models.IntegerField(
        help_text="HP after str modification",
        default=150,
        editable=False
    )
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
    atk_backswing = models.FloatField(default=0)
    cast_point = models.FloatField(default=0)
    cast_backswing = models.FloatField(default=0)
    turn_rate = models.FloatField()
    legs = models.IntegerField(default=0)

    def __unicode__(self):
        return self.hero.name

    def level_stat(self, stat, level):
        if stat == 'level':
            return level
        elif stat == 'strength':
            return self.strength + (level-1)*self.strength_gain
        elif stat == 'agility':
            return self.agility + (level-1)*self.agility_gain
        elif stat == 'intelligence':
            return self.intelligence + (level-1)*self.intelligence_gain
        elif stat == 'armor':
            return self.armor + (level-1)*self.agility_gain/7
        elif stat == 'hp':
            return self.hp+(level-1)*self.strength_gain*19
        elif stat == 'effective_hp':
            return (
                (1 + 0.06 * (self.level_stat('armor', level)))
                * self.level_stat('hp', level)
            )
        elif stat == 'mana':
            return self.mana+(level-1)*self.intelligence_gain*13
        else:
            raise Exception("{0},{1},{2}, buh?".format(self, stat, level))

    def fetch_value(self, stat, level):
        easy_list = [
            'day_vision',
            'night_vision',
            'atk_point',
            'atk_backswing',
            'cast_point',
            'cast_backswing',
            'turn_rate',
            'legs',
            'movespeed',
            'projectile_speed',
            'range',
            'base_atk_time',
            'strength_gain',
            'agility_gain',
            'intelligence_gain',
        ]
        if level not in range(1, 26):
            raise AttributeError("That is not a real level")
        if hasattr(self, stat) and stat in easy_list:
            return getattr(self, stat)
        elif stat == "strength":
            return self.strength+(level-1)*self.strength_gain
        elif stat == "intelligence":
            return self.intelligence+(level-1)*self.intelligence_gain
        elif stat == "agility":
            return self.agility+(level-1)*self.agility_gain
        elif stat == "modified_armor":
            return self.armor + ((level-1)*self.agility_gain)/7.0
        elif stat == "effective_hp":
            armor = self.armor + ((level-1)*self.agility_gain)/7.0
            strength_add = (level-1)*self.strength_gain
            hp = self.hp + strength_add*19
            return (1+0.06*armor) * hp
        elif stat == 'hp':
            strength_add = (level-1)*self.strength_gain
            hp = self.hp + strength_add*19
            return hp
        elif stat == 'mana':
            intelligence_add = (level-1)*self.intelligence_gain
            mana = self.mana + intelligence_add*13
            return mana
        elif stat == "hp_regen":
            return self.hp_regen + ((level-1)*self.strength_gain)*0.03
        elif stat == "mana_regen":
            return self.mana_regen + self.fetch_value(
                'intelligence', level
                )*0.04
        elif stat == "damage":
            base_dmg = (self.max_dmg + self.min_dmg) / 2
            if self.alignment == 'intelligence':
                add_dmg = (level-1)*self.intelligence_gain
            elif self.alignment == 'strength':
                add_dmg = (level-1)*self.strength_gain
            elif self.alignment == 'agility':
                add_dmg = (level-1)*self.agility_gain
            return base_dmg + add_dmg

        else:
            raise AttributeError("What is %s" % stat)


def invalid_option(stats_list):
    valid_stat_set = set([
        'level',
        'strength',
        'agility',
        'intelligence',
        'armor',
        'hp',
        'effective_hp',
        'mana',
    ])
    for stat in stats_list:
        if stat not in valid_stat_set:
            return True
    return False


def safen(str):
    return str.replace('-', ' ').replace('_', ' ').title()


def human_name(str):
    return str.replace("_", " ").title()
