from model_mommy.recipe import Recipe, seq, foreign_key
from model_mommy import mommy
from itertools import cycle

from heroes.models import Hero, Role, Assignment, HeroDossier, Ability

roles = [
    u'Nuker',
    u'Disabler',
    u'Escape',
    u'Initiator',
    u'Support',
    u'Jungler',
    u'Pusher',
    u'Durable',
    u'LaneSupport',
    u'Carry',
]

alignments = ['strength', 'intelligence', 'agility']

role = Recipe(
    Role,
    name=cycle(roles)
    # name=u'nuker'
    )

ability = Recipe(
    Ability,
    name=seq('Ability'),
    steam_id=seq(1)
    )


hero = Recipe(
    Hero,
    visible=True,
    name=seq('Hero'),
    steam_id=seq(1),
)

assignment = Recipe(
    Assignment,
    role=foreign_key(role),
    hero=foreign_key(hero),
    magnitude=cycle(range(1, 4))
    )

herodossier = Recipe(
    HeroDossier,
    hero=foreign_key(hero),
    alignment=cycle(alignments)
    )


def make_hero(steam_id=None):
    if steam_id is not None:
        hero = mommy.make_recipe('heroes.hero', steam_id=steam_id)
    else:
        hero = mommy.make_recipe('heroes.hero')

    a1 = mommy.make_recipe(
        'heroes.assignment',
        hero=hero)

    h1 = a1.hero
    mommy.make_recipe('heroes.herodossier', hero=h1)
    mommy.make_recipe('heroes.ability', hero=h1, _quantity=4)
    return h1
