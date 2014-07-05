import datetime
from django.conf import settings
from django.db.models import Count
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from matches.models import PlayerMatchSummary, GameMode, Match
from .models import Player
from utils.exceptions import NoDataFound
from itertools import chain
from utils.charts import (
    hero_classes_dict,
    XYPlot,
    DataPoint,
    TasselPlot,
    TasselDataPoint
)
from heroes.models import Hero, Role, HeroDossier
from matches.models import SkillBuild
from collections import defaultdict
from time import mktime

if settings.VERBOSE_PROFILING:
    try:
        from line_profiler import LineProfiler

        def do_profile(follow=[]):
            def inner(func):
                def profiled_func(*args, **kwargs):
                    try:
                        profiler = LineProfiler()
                        profiler.add_function(func)
                        for f in follow:
                            profiler.add_function(f)
                        profiler.enable_by_count()
                        return func(*args, **kwargs)
                    finally:
                        profiler.print_stats()
                return profiled_func
            return inner

    except ImportError:
        def do_profile(follow=[]):
            "Helpful if you accidentally leave in production!"
            def inner(func):
                def nothing(*args, **kwargs):
                    return func(*args, **kwargs)
                return nothing
            return inner
else:
    def do_profile(follow=[]):
        "Helpful if you accidentally leave in production!"
        def inner(func):
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)
            return nothing
        return inner


@do_profile()
def player_winrate_json(
        player,
        game_modes=None,
        role_list=[],
        min_date=None,
        max_date=None,
        group_var='alignment',
        ):
    if max_date is None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    if min_date is None:
        min_date_utc = mktime(datetime.date(2009, 1, 1).timetuple())
    else:
        min_date_utc = mktime(min_date.timetuple())

    if min_date_utc > max_date_utc:
        raise NoDataFound
    if game_modes is None:
        game_modes = [
            gm.steam_id
            for gm in GameMode.objects.filter(is_competitive=True)
        ]

    try:
        player = Player.objects.get(steam_id=player)
    except Player.DoesNotExist:
        raise NoDataFound
    annotations = PlayerMatchSummary.objects.filter(
        player=player,
        match__validity=Match.LEGIT,
        match__start_time__gte=min_date_utc,
        match__start_time__lte=max_date_utc,
        match__game_mode__steam_id__in=game_modes,
    )
    if role_list != []:
        roles = Role.objects.filter(name__in=role_list)
        annotations = annotations.filter(hero__roles__in=roles)

    annotations = annotations.values('hero__name', 'is_win')\
        .annotate(Count('is_win'))

    if len(annotations) == 0:
        raise NoDataFound

    heroes = list(set([row['hero__name'] for row in annotations]))
    wins = defaultdict(int)
    losses = defaultdict(int)

    for row in annotations:
        if row['is_win']:
            wins[row['hero__name']] += 1
        else:
            losses[row['hero__name']] += 1

    win_rates = {hero: float(wins.get(hero, 0)) / (wins.get(hero, 0)
        + losses.get(hero, 0)) * 100
        for hero in heroes
    }
    games = {hero: wins.get(hero, 0) + losses.get(hero, 0) for hero in heroes}

    hero_classes = hero_classes_dict()
    all_heroes = Hero.public.values(
        'machine_name',
        'name',
        'herodossier__alignment',
        'steam_id',
        )
    hero_info_dict = {hero['name']:
                        {
                            'name': hero['name'],
                            'machine_name': hero['machine_name'],
                            'alignment': hero['herodossier__alignment'],
                            'steam_id': hero['steam_id'],
                        } for hero in all_heroes
    }

    c = XYPlot()
    for hero in heroes:
        if group_var == 'hero':
            group = hero_info_dict[hero]['name']
        elif group_var == 'alignment':
            group = hero_info_dict[hero]['alignment'].title()

        url_str = reverse(
            'players:hero_style',
            kwargs={
                'hero_name': hero_info_dict[hero]['machine_name'],
                'player_id': player,
            }
        )

        d = DataPoint()

        d.x_var = games[hero]
        d.y_var = round(win_rates[hero], 2)
        d.group_var = group
        d.url = url_str
        d.label = hero
        d.tooltip = hero
        d.classes = []
        if hero_classes[hero_info_dict[hero]['steam_id']] is not None:
            d.classes.extend(
                hero_classes[hero_info_dict[hero]['steam_id']]
            )

        c.datalist.append(d)

    if group_var != 'alignment':
        c.params.draw_legend = False

    c.params.y_max = 100
    c.params.y_min = 0
    c.params.x_min = 0
    c.params.x_label = 'Games'
    c.params.y_label = 'Winrate'
    c.params.draw_path = False
    c.params.margin['left'] = 24
    c.params.outerWidth = 300
    c.params.outerHeight = 300
    c.params.legendWidthPercent = .7
    c.params.legendHeightPercent = .7
    return c


@do_profile()
def player_hero_abilities_json(
        player_1,
        hero_1,
        player_2,
        hero_2,
        game_modes,
        division=None
        ):

    p1 = Player.objects.get(steam_id=player_1)
    h1 = Hero.public.get(steam_id=hero_1)
    sb1 = SkillBuild.objects.filter(
        player_match_summary__hero=h1,
        player_match_summary__player=p1,
    ).values(
        'time',
        'level',
        'player_match_summary__is_win',
        'player_match_summary__match__steam_id',
        'player_match_summary__hero__steam_id',
        'player_match_summary__player__persona_name',
        'player_match_summary__player__pro_name',
    ).order_by('player_match_summary', 'level')
    if player_2 is not None and hero_2 is not None:
        p2 = Player.objects.get(steam_id=player_2)
        h2 = Hero.public.get(steam_id=hero_2)

        sb2 = SkillBuild.objects.filter(
            player_match_summary__hero=h2,
            player_match_summary__player=p2,
        ).values(
            'time',
            'level',
            'player_match_summary__is_win',
            'player_match_summary__match__steam_id',
            'player_match_summary__hero__steam_id',
            'player_match_summary__player__persona_name',
            'player_match_summary__player__pro_name',
        ).distinct().order_by('player_match_summary', 'level')
        sbs = chain(sb1, sb2)
    elif player_2 is None and hero_2 is None:
        sbs = sb1
    else:
        raise NoDataFound

    hero_classes = hero_classes_dict()

    c = TasselPlot()
    for build in sbs:

        name = build['player_match_summary__player__persona_name']
        pro_name = build['player_match_summary__player__pro_name']
        display_name = pro_name if pro_name is not None else name

        if build['level'] == 1:
            subtractor = build['time']/60.0

        d = TasselDataPoint()
        d.x_var = round(build['time']/60.0-subtractor, 3)
        d.y_var = build['level']

        winningness = 'Win' if \
            build['player_match_summary__is_win'] \
            else 'Loss'

        if division == 'Player win/loss':
            group = "{p}, ({win})".format(
                p=display_name,
                win=winningness)
        elif division == 'Players':
            group = "{p}".format(
                p=display_name)
        elif division == 'Win/loss':
            group = "{win}".format(
                win=winningness)

        d.group_var = group

        d.series_var = build['player_match_summary__match__steam_id']

        d.label = display_name

        d.panel_var = 'Skill Progression'

        hero_id = build['player_match_summary__hero__steam_id']

        if hero_classes[hero_id] is not None:
            d.classes.extend(hero_classes[hero_id])

        c.datalist.append(d)

    c.params.x_min = 0
    c.params.x_label = 'Time (m)'
    c.params.y_label = 'Level'

    return c


@do_profile()
def player_versus_winrate_json(
        player_1,
        player_2,
        game_modes=None,
        min_date=None,
        max_date=None,
        group_var='alignment',
        plot_var='winrate',
        ):
    if max_date is None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    if min_date is None:
        min_date_utc = mktime(datetime.date(2009, 1, 1).timetuple())
    else:
        min_date_utc = mktime(min_date.timetuple())

    hero_classes = hero_classes_dict()

    if min_date_utc > max_date_utc:
        raise NoDataFound
    if game_modes is None:
        game_modes = [
            gm.steam_id
            for gm in GameMode.objects.filter(is_competitive=True)
        ]

    try:
        player_1_obj = Player.objects.get(steam_id=player_1)
        player_2_obj = Player.objects.get(steam_id=player_2)

    except Player.DoesNotExist:
        raise NoDataFound

    pmses = PlayerMatchSummary.objects.filter(
        player__steam_id__in=[player_1, player_2],
        match__validity=Match.LEGIT,
        match__start_time__gte=min_date_utc,
        match__start_time__lte=max_date_utc,
        match__game_mode__steam_id__in=game_modes,
    ).values(
        'hero__name',
        'is_win',
        'player__steam_id',
    ).distinct()

    if len(pmses) == 0:
        raise NoDataFound

    pairings = {}
    for pms in pmses:
        if pms['hero__name'] not in pairings:
            pairings[pms['hero__name']] = {
                player_1: {'wins': 0, 'losses': 0},
                player_2: {'wins': 0, 'losses': 0},
            }
        if pms['is_win']:
            pairings[pms['hero__name']][pms['player__steam_id']]['wins'] += 1
        else:
            pairings[pms['hero__name']][pms['player__steam_id']]['losses'] += 1

    for hero in pairings.iterkeys():

        pairings[hero][player_1]['total_games'] = \
            pairings[hero][player_1]['wins'] \
            + pairings[hero][player_1]['losses']
        if pairings[hero][player_1]['total_games'] != 0:
            pairings[hero][player_1]['winrate'] = \
                float(pairings[hero][player_1]['wins'])\
                / pairings[hero][player_1]['total_games']*100
        else:
            pairings[hero][player_1]['winrate'] = 0

        pairings[hero][player_2]['total_games'] = \
            pairings[hero][player_2]['wins'] \
            + pairings[hero][player_2]['losses']

        if pairings[hero][player_2]['total_games'] != 0:
            pairings[hero][player_2]['winrate'] = \
                float(pairings[hero][player_2]['wins'])\
                / pairings[hero][player_2]['total_games']*100
        else:
            pairings[hero][player_2]['winrate'] = 0

    all_heroes = Hero.public.values(
        'machine_name',
        'name',
        'herodossier__alignment',
        'steam_id',
        )
    hero_info_dict = {hero['name']:
                    {
                        'name': hero['name'],
                        'machine_name': hero['machine_name'],
                        'alignment': hero['herodossier__alignment'],
                        'steam_id': hero['steam_id'],
                    } for hero in all_heroes
    }

    c = XYPlot()
    for hero_name, dataset in pairings.iteritems():
        d = DataPoint()
        if group_var == 'hero':
            group = hero_info_dict[hero_name]['name']
        elif group_var == 'alignment':
            group = hero_info_dict[hero_name]['alignment'].title()
            d.group_var = group
            d.label = hero_info_dict[hero_name]['name']
            d.tooltip = hero_info_dict[hero_name]['name']

        if hero_classes[hero_info_dict[hero_name]['steam_id']] is not None:
            d.classes.extend(hero_classes[hero_info_dict[
                hero_name]['steam_id']
                ])
        d.point_size = min(
            dataset[player_1]['total_games'],
            dataset[player_2]['total_games']
            )
        d.stroke_width = 2
        if plot_var == 'winrate':

            d.x_var = dataset[player_1]['winrate']
            d.y_var = dataset[player_2]['winrate']
        else:
            d.x_var = dataset[player_1]['total_games']
            d.y_var = dataset[player_2]['total_games']

        c.datalist.append(d)
    c.params.x_label = "{name} {pvar}".format(
        name=player_1_obj.display_name,
        pvar=plot_var,
    )
    c.params.y_label = "{name} {pvar}".format(
        name=player_2_obj.display_name,
        pvar=plot_var,
    )
    c.params.pointDomainMin = 0
    c.params.pointDomainMax = 10
    c.params.pointSizeMin = 2
    c.params.pointSizeMax = 5
    c.params.strokeSizeMin = 1
    c.params.strokeSizeMax = 1

    if plot_var == 'winrate':
        c.params.y_max = 100
        c.params.x_max = 100
        c.params.strokeDomainMin = 0
        c.params.strokeDomainMax = 1
    if group_var == 'hero':
        c.params.draw_legend = False
    elif group_var == 'alignment':
        c.params.draw_legend = True

    return c


@do_profile()
def player_hero_side_json(
        player,
        game_modes=None,
        min_date=datetime.date(2009, 1, 1),
        max_date=None,
        group_var='alignment',
        plot_var='winrate',
):

    if max_date is None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    if min_date is None:
        min_date_utc = mktime(datetime.date(2009, 1, 1).timetuple())
    else:
        min_date_utc = mktime(min_date.timetuple())

    if min_date_utc > max_date_utc:
        raise NoDataFound

    all_heroes = Hero.public.all()
    hero_names = {h.name: h for h in all_heroes}

    if game_modes is None:
        game_modes = [
            gm.steam_id
            for gm in GameMode.objects.filter(is_competitive=True)
        ]

    try:
        player = Player.objects.get(steam_id=player)

    except Player.DoesNotExist:
        raise NoDataFound

    player_radiant_matches = Match.objects.filter(
        playermatchsummary__player=player,
        validity=Match.LEGIT,
        start_time__gte=min_date_utc,
        start_time__lte=max_date_utc,
        game_mode__steam_id__in=game_modes,
        playermatchsummary__player_slot__lt=6,
    ).distinct()

    player_dire_matches = Match.objects.filter(
        playermatchsummary__player=player,
        validity=Match.LEGIT,
        start_time__gte=min_date_utc,
        start_time__lte=max_date_utc,
        game_mode__steam_id__in=game_modes,
        playermatchsummary__player_slot__gt=6,
    ).distinct()

    oppose_radiant_pmses = PlayerMatchSummary.objects.filter(
        match__in=player_radiant_matches,
        player_slot__gte=6,
        ).exclude(
        player=player).values('hero__name', 'is_win')\
        .annotate(Count('id')).order_by()

    oppose_dire_pmses = PlayerMatchSummary.objects.filter(
        match__in=player_dire_matches,
        player_slot__lte=6,
        ).exclude(
        player=player).values('hero__name', 'is_win')\
        .annotate(Count('id')).order_by()

    sameside_radiant_pmses = PlayerMatchSummary.objects.filter(
        match__in=player_radiant_matches,
        player_slot__lte=6,
        ).exclude(
        player=player).values('hero__name', 'is_win')\
        .annotate(Count('id')).order_by()

    sameside_dire_pmses = PlayerMatchSummary.objects.filter(
        match__in=player_dire_matches,
        player_slot__gte=6,
        ).exclude(
        player=player).values('hero__name', 'is_win')\
        .annotate(Count('id')).order_by()

    outcome_dict = {}
    for minidict in chain(oppose_radiant_pmses, oppose_dire_pmses):
        if minidict['hero__name'] not in outcome_dict.iterkeys():
            outcome_dict[minidict['hero__name']] = {
                'same_side': {
                    'total_games': 0,
                    'wins': 0,
                    'winrate': 0,
                    'losses': 0,
                },
                'opposite_side': {
                    'total_games': 0,
                    'wins': 0,
                    'winrate': 0,
                    'losses': 0,
                }
            }
        if minidict['is_win']:
            idx = 'wins'
        else:
            idx = 'losses'
        outcome_dict[minidict['hero__name']]['opposite_side'][idx] \
            += minidict['id__count']

    for minidict in chain(sameside_radiant_pmses, sameside_dire_pmses):
        if minidict['hero__name'] not in outcome_dict.iterkeys():
            outcome_dict[minidict['hero__name']] = \
                {
                    'same_side': {
                        'total_games': 0,
                        'wins': 0,
                        'winrate': 0,
                        'losses': 0,
                    },
                    'opposite_side': {
                        'total_games': 0,
                        'wins': 0,
                        'winrate': 0,
                        'losses': 0,
                    }
                }
        if minidict['is_win']:
            idx = 'wins'
        else:
            idx = 'losses'
        outcome_dict[minidict['hero__name']]['same_side'][idx] \
            += minidict['id__count']

    if outcome_dict == {}:
        raise NoDataFound

    for hero, dct in outcome_dict.iteritems():
        for side, gamedct in dct.iteritems():
            gamedct['total_games'] = gamedct['wins'] + gamedct['losses']
            denominator = 1 if gamedct['total_games'] == 0 \
                else gamedct['total_games']
            gamedct['winrate'] = gamedct['wins']/float(denominator)*100

    hero_classes = hero_classes_dict()
    c = XYPlot()
    for name, dataset in outcome_dict.iteritems():
        hero = hero_names[name]
        d = DataPoint()
        if group_var == 'hero':
            group = hero.name.title()
        elif group_var == 'alignment':
            try:
                group = hero.herodossier.alignment.title()
            except HeroDossier.DoesNotExist:
                group = ''

        d.group_var = group
        d.label = hero.name
        d.tooltip = hero.name
        if hero_classes[hero.steam_id] is not None:
            d.classes.extend(hero_classes[hero.steam_id])

        if plot_var == 'winrate':
            d.point_size = dataset['same_side']['total_games']
            d.stroke_width = dataset['opposite_side']['total_games']

            d.x_var = dataset['same_side']['winrate']
            d.y_var = dataset['opposite_side']['winrate']
        else:
            d.point_size = \
                (dataset['same_side']['total_games']
                    + dataset['opposite_side']['total_games'])/2.0
            d.x_var = dataset['same_side']['total_games']
            d.y_var = dataset['opposite_side']['total_games']

        c.datalist.append(d)

    c.params.x_label = "Same-side {pvar}".format(
        pvar=plot_var,
    )
    c.params.y_label = "Opposite-side {pvar}".format(
        pvar=plot_var,
    )
    c.params.margin['left'] = 35
    c.params.pointDomainMin = 0
    c.params.pointDomainMax = 10
    c.params.pointSizeMin = 1
    c.params.pointSizeMax = 5

    if plot_var == 'winrate':
        c.params.y_min = 0
        c.params.x_min = 0
        c.params.y_max = 100
        c.params.x_max = 100
        c.params.strokeDomainMin = 0
        c.params.strokeDomainMax = 10
        c.params.strokeSizeMin = 0
        c.params.strokeSizeMax = 2
    if group_var == 'hero':
        c.params.draw_legend = False
    elif group_var == 'alignment':
        c.params.draw_legend = True

    return c


@do_profile()
def player_role_json(
    player_1,
    player_2=None,
    plot_var='performance',
):

    player_id_list = [player_1]
    p1_obj = Player.objects.get(steam_id=player_1)
    if player_2 is not None:
        player_id_list.append(player_2)
        p2_obj = Player.objects.get(steam_id=player_2)

    role_annotations = PlayerMatchSummary.objects.filter(
        match__validity=Match.LEGIT,
        player__steam_id__in=player_id_list,
    ).values(
        'hero__assignment__role__name', 'is_win', 'player__steam_id'
    ).annotate(Count('player_slot')).order_by()

    role_dict = {}

    for annotation in role_annotations:
        role = annotation['hero__assignment__role__name']
        if role is None:
            continue

        player = annotation['player__steam_id']
        if role not in role_dict:
            role_dict[role] = {}
            role_dict[role][player_1] = {True: 0, False: 0}
            role_dict[role][player_2] = {True: 0, False: 0}
        is_win = annotation['is_win']
        games = annotation['player_slot__count']
        role_dict[role][player][is_win] = games
    for role, minidict in role_dict.iteritems():
        for player, subdict in minidict.iteritems():
            subdict['games'] = subdict[True] + subdict[False]
            denominator = subdict['games'] if subdict['games'] != 0 else 1
            subdict['winrate'] = subdict[True] / float(denominator) * 100

    c = XYPlot()
    for role, info in role_dict.iteritems():

        if plot_var == 'performance':
            for player_id, data in info.iteritems():
                d = DataPoint()
                d.group_var = player_id
                d.label = role
                d.tooltip = role
                d.x_var = data['games']
                d.y_var = data['winrate']
                d.classes.extend([slugify(role)])
                x_label = "Games"
                y_label = "Winrate"

        elif plot_var == 'games':
                d = DataPoint()
                d.group_var = role
                d.panel_var = ''
                d.label = role
                d.tooltip = role
                d.x_var = info[player_1]['games']
                d.y_var = info[player_2]['games']
                d.classes.extend([slugify(role)])
                x_label = "{p} Games".format(p=p1_obj.display_name)
                y_label = "{p} Games".format(p=p2_obj.display_name)

        elif plot_var == 'winrate':
                d = DataPoint()
                d.group_var = role
                d.panel_var = ''
                d.label = role
                d.tooltip = role
                d.x_var = info[player_1]['winrate']
                d.y_var = info[player_2]['winrate']
                d.classes.extend([slugify(role)])
                x_label = "{p} Winrate".format(p=p1_obj.display_name)
                y_label = "{p} Winrate".format(p=p2_obj.display_name)
        c.datalist.append(d)

    c.params.x_ticks = 7
    c.params.x_ticks = 7
    c.params.x_label = x_label
    c.params.y_label = y_label

    return c
