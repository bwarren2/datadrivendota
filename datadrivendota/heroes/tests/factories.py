from factory.django import DjangoModelFactory
from factory import SubFactory, Sequence, LazyAttribute
from factory.fuzzy import FuzzyInteger, FuzzyChoice

from django.utils.text import slugify

from heroes.models import (
    Hero,
    HeroDossier,
    Role,
    Ability
)


class HeroFactory(DjangoModelFactory):
    FACTORY_FOR = Hero

    name = Sequence(lambda n: u'Hero{0}'.format(n))
    machine_name = Sequence(lambda n: u'hero{0}'.format(n))
    internal_name = LazyAttribute(lambda obj: slugify(obj.name))
    steam_id = Sequence(lambda n: n + 1)
    lore = 'my lore'
    visible = True


class RoleFactory(DjangoModelFactory):
    FACTORY_FOR = Role
    NAMES = [
        'LaneSupport',
        'Carry',
        'Disabler',
        'Ganker',
        'Nuker',
        'Initiator',
        'Jungler',
        'Pusher',
        'Roamer',
        'Durable',
        'Escape',
        'Support',
    ]
    name = FuzzyChoice(NAMES)
    machine_name = Sequence(lambda n: u'hero{0}'.format(n))
    desc = Sequence(lambda n: u'hero{0}'.format(n))


class HeroDossierFactory(DjangoModelFactory):
    FACTORY_FOR = HeroDossier

    hero = SubFactory(HeroFactory)
    movespeed = FuzzyInteger(0, 500)
    max_dmg = FuzzyInteger(0, 500)
    min_dmg = FuzzyInteger(0, 500)
    hp = FuzzyInteger(0, 500)
    mana = FuzzyInteger(0, 500)
    hp_regen = FuzzyInteger(0, 500)
    mana_regen = FuzzyInteger(0, 500)
    armor = FuzzyInteger(0, 500)
    range = FuzzyInteger(0, 500)
    projectile_speed = FuzzyInteger(0, 500)
    strength = FuzzyInteger(0, 50)
    agility = FuzzyInteger(0, 50)
    intelligence = FuzzyInteger(0, 50)
    strength_gain = FuzzyInteger(0, 5)
    agility_gain = FuzzyInteger(0, 5)
    intelligence_gain = FuzzyInteger(0, 5)
    alignment = FuzzyChoice(['strength', 'intelligence', 'agility'])
    base_atk_time = FuzzyInteger(0, 500)
    day_vision = FuzzyInteger(0, 500)
    night_vision = FuzzyInteger(0, 500)
    atk_point = FuzzyInteger(0, 500)
    atk_backswing = FuzzyInteger(0, 500)
    cast_point = FuzzyInteger(0, 500)
    cast_backswing = FuzzyInteger(0, 500)
    turn_rate = FuzzyInteger(0, 500)
    legs = FuzzyInteger(0, 500)


class AbilityFactory(DjangoModelFactory):
    class Meta:
        model = Ability
