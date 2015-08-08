from django.templatetags.static import static
from django.db import models
from django.utils.text import slugify
from .managers import VisibleHeroManager
from utils import safen


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
    def thumbshot_url(self):
        return self.thumbshot.url or static('blank_role.png')

    @property
    def url(self):
        return "images/pips/{}.png".format(self.name.lower())

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.machine_name = slugify(self.name)
        super(Role, self).save(*args, **kwargs)


class Hero(models.Model):
    steam_id = models.PositiveIntegerField(
        unique=True,
        help_text="Valve's int"
    )
    name = models.CharField(
        max_length=200,
        help_text="In-game name."
    )
    machine_name = models.SlugField(
        max_length=200,
        help_text="What goes in URLs.  See slugify()",
        blank=True,
    )
    internal_name = models.CharField(
        max_length=200,
        help_text="The protobuf string for the hero"
    )
    lore = models.TextField(null=True)
    mugshot = models.ImageField(
        null=True,
        upload_to='heroes/img/',
        default='blanks/blank_hero_mugshot.png'
    )
    thumbshot = models.ImageField(
        null=True,
        upload_to='heroes/img/',
        default='blanks/blank_hero_thumb.png'
    )
    visible = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, through='Assignment')

    objects = models.Manager()
    public = VisibleHeroManager()

    @property
    def thumbshot_url(self):
        try:
            return self.thumbshot.url
        except ValueError:
            return static('blank_hero_thumb.png')

    @property
    def mugshot_url(self):
        try:
            return self.mugshot.url
        except ValueError:
            return static('blank_hero_mugshot.png')

    @property
    def has_image(self):
        """ Used on hero import to check who is visible. """
        return hasattr(self.thumbshot, 'url')

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
    steam_id = models.IntegerField(
        help_text="Valve's internal map",
        unique=True
    )
    internal_name = models.CharField(
        help_text="Valve's underscore name",
        max_length=150
    )
    machine_name = models.CharField(
        help_text="Valve's underscore name, slugified",
        max_length=150,
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

    # Things that come from the jsfeed http://www.dota2.com/jsfeed/abilitydata
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
        return "{0} ({1})".format(
            self.internal_name,
            str(self.steam_id)
        )

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
        return "{0} ({1})".format(
            str(self.key),
            str(self.value)
        )


class AbilityBehavior(models.Model):
    internal_name = models.CharField(
        help_text="Valve's all-caps underscore name",
        max_length=150
    )

    def __unicode__(self):
        return safen(self.internal_name)

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
        return safen(self.internal_name)


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
        return safen(self.internal_name)


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
        return safen(self.internal_name)


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
