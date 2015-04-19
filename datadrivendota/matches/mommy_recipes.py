from django.utils import timezone
from time import mktime
from model_mommy.recipe import Recipe, seq, foreign_key
from model_mommy import mommy
from .models import Match, PlayerMatchSummary, GameMode
from heroes.mommy_recipes import hero, make_hero
from players.mommy_recipes import player
from items.mommy_recipes import item
from heroes.models import Ability

match = Recipe(
    Match,
    steam_id=seq(1),
    )

game_mode = Recipe(
    GameMode,
    is_competitive=True
)

playermatchsummary = Recipe(
    PlayerMatchSummary,
    match=foreign_key(match),
    hero=foreign_key(hero),
    player=foreign_key(player),
    item_0=foreign_key(item),
    item_1=foreign_key(item),
    item_2=foreign_key(item),
    item_3=foreign_key(item),
    item_4=foreign_key(item),
    item_5=foreign_key(item),
    )


def make_pmses(hero=None, player=None, skill=0, qty=1):
    if hero is None:
        hero_id = 1
    if player is None:
        player_id = 1
    i = mommy.make_recipe('items.item', name='')
    h = mommy.make_recipe('heroes.hero', steam_id=hero_id)
    p = mommy.make_recipe('players.player', steam_id=player_id)
    ls = mommy.make('matches.leaverstatus', )
    gm = mommy.make_recipe('matches.game_mode')
    mommy.make(
        'matches.playermatchsummary',
        player=p,
        hero=h,
        item_0=i,
        item_1=i,
        item_2=i,
        item_3=i,
        item_4=i,
        item_5=i,
        leaver=ls,
        match__game_mode=gm,
        match__validity=Match.LEGIT,
        _quantity=qty,
    )
    return h, p


def make_skill_pmses(hero=None, player=None, qty=1):
    if hero is None:
        hero_id = 1
    if player is None:
        player_id = 1

    i = mommy.make_recipe('items.item', name='')
    h = mommy.make_recipe('heroes.hero', steam_id=hero_id)
    p = mommy.make_recipe('players.player', steam_id=player_id)
    ls = mommy.make('matches.leaverstatus')
    gm = mommy.make_recipe('matches.game_mode')
    ab = mommy.make('heroes.ability', name='Ab1')
    ab2 = mommy.make('heroes.ability', name='Ab2')
    sb = mommy.make('matches.skillbuild', level=1, ability=ab)
    sb2 = mommy.make('matches.skillbuild', level=2, ability=ab2)

    for skill in range(0, 5):
        mommy.make(
            'matches.playermatchsummary',
            player=p,
            hero=h,
            item_0=i,
            item_1=i,
            item_2=i,
            item_3=i,
            item_4=i,
            item_5=i,
            leaver=ls,
            match=foreign_key(match),
            match__game_mode=gm,
            match__skill=skill,
            match__validity=Match.LEGIT,
            skillbuild_set=[sb, sb2],
            _quantity=qty,
        )
    return h, p


def make_matchset():

    # Make a hero
    h = make_hero()

    i = mommy.make('items.item', thumbshot=None, mugshot=None)
    p = mommy.make(
        'players.player',
        pro_name='ProGuy')
    ls = mommy.make('matches.leaverstatus')
    lt = mommy.make('matches.lobbytype')
    gm = mommy.make_recipe('matches.game_mode')

    from teams.models import Team
    try:
        t = Team.objects.get(steam_id=1333179)
    except Team.DoesNotExist:
        t = mommy.make(
            'teams.team',
            steam_id=1333179,
            name='FakeTI4 team',
            player_0=p
        )
    l = mommy.make('leagues.league')
    abilities = Ability.objects.filter(hero=h)

    sb = mommy.make('matches.skillbuild', level=1, ability=abilities[0])
    sb2 = mommy.make('matches.skillbuild', level=2, ability=abilities[1])
    sb3 = mommy.make('matches.skillbuild', level=3, ability=abilities[0])

    start_time = mktime(timezone.now().timetuple())
    print start_time
    for skill in range(0, 5):
        mommy.make(
            'matches.playermatchsummary',
            player=p,
            hero=h,
            item_0=i,
            item_1=i,
            item_2=i,
            item_3=i,
            item_4=i,
            item_5=i,
            leaver=ls,
            level=3,
            match__radiant_team=t,
            match__league=l,
            match__game_mode=gm,
            match__start_time=start_time,
            match__lobby_type=lt,
            match__skill=skill,
            match__validity=Match.LEGIT,
            skillbuild_set=[sb, sb2, sb3],
            _quantity=3,
        )
    # Ensure there is always 1 win and 1 loss
    # Tests can be nondeterministic otherwise
    mommy.make(
        'matches.playermatchsummary',
        player=p,
        hero=h,
        item_0=i,
        item_1=i,
        item_2=i,
        item_3=i,
        item_4=i,
        item_5=i,
        leaver=ls,
        level=3,
        match__radiant_team=t,
        match__league=l,
        match__game_mode=gm,
        match__start_time=start_time,
        match__lobby_type=lt,
        match__skill=1,
        is_win=True,
        match__validity=Match.LEGIT,
        skillbuild_set=[sb, sb2, sb3],
        _quantity=1,
    )
    mommy.make(
        'matches.playermatchsummary',
        player=p,
        hero=h,
        item_0=i,
        item_1=i,
        item_2=i,
        item_3=i,
        item_4=i,
        item_5=i,
        leaver=ls,
        level=3,
        match__radiant_team=t,
        match__league=l,
        match__game_mode=gm,
        match__start_time=start_time,
        match__lobby_type=lt,
        match__skill=1,
        is_win=False,
        match__validity=Match.LEGIT,
        skillbuild_set=[sb, sb2, sb3],
        _quantity=1,
    )

    return h, p
