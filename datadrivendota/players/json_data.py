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
    params_dict,
    datapoint_dict,
    color_scale_params,
    hero_classes_dict
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
        min_date=datetime.date(2009, 1, 1),
        max_date=None,
        group_var='alignment',
        ):
    if max_date is None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    min_dt_utc = mktime(min_date.timetuple())

    if min_dt_utc > max_date_utc:
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
        match__start_time__gte=min_dt_utc,
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
    all_heroes = Hero.objects.filter(visible=True).values(
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

    data_list, groups = [], []
    for hero in heroes:
        datadict = datapoint_dict()
        if group_var == 'hero':
            group = hero_info_dict[hero]['name']
        elif group_var == 'alignment':
            group = hero_info_dict[hero]['alignment'].title()
        groups.append(group)

        url_str = reverse(
            'players:hero_style',
            kwargs={
                'hero_name': hero_info_dict[hero]['machine_name'],
                'player_id': player,
            }
        )

        datadict.update({
            'x_var': games[hero],
            'y_var': round(win_rates[hero], 2),
            'group_var': group,
            'split_var': '',
            'url': url_str,
            'label': hero,
            'tooltip': hero,
            'classes': [],
        })
        if hero_classes[hero_info_dict[hero]['steam_id']] is not None:
            datadict['classes'].extend(
                hero_classes[hero_info_dict[hero]['steam_id']]
            )

        data_list.append(datadict)

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in data_list])
    params['x_max'] = max([d['x_var'] for d in data_list])
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = 100
    params['x_label'] = 'Games'
    params['y_label'] = 'Winrate'
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['outerWidth'] = 500
    params['outerHeight'] = 500
    params['legendWidthPercent'] = .7
    params['legendHeightPercent'] = .7
    groups = [d['group_var'] for d in data_list]
    if group_var == 'hero':
        params['draw_legend'] = False
    elif group_var == 'alignment':
        params['draw_legend'] = True
    params = color_scale_params(params, groups)

    return (data_list, params)


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
    h1 = Hero.objects.get(steam_id=hero_1)
    sb1 = SkillBuild.objects.filter(
        player_match_summary__hero=h1,
        player_match_summary__player=p1,
    ).select_related().order_by('player_match_summary', 'level')
    if player_2 is not None and hero_2 is not None:
        p2 = Player.objects.get(steam_id=player_2)
        h2 = Hero.objects.get(steam_id=hero_2)

        sb2 = SkillBuild.objects.filter(
            player_match_summary__hero=h2,
            player_match_summary__player=p2,
        ).select_related().order_by('player_match_summary', 'level')
        sbs = chain(sb1, sb2)
    elif player_2 is None and hero_2 is None:
        sbs = sb1
    else:
        raise NoDataFound
    datalist = []
    xs = []
    ys = []
    hero_classes = hero_classes_dict()
    for build in sbs:
        if build.level == 1:
            subtractor = build.time/60.0
        datapoint = datapoint_dict()
        datapoint['x_var'] = round(build.time/60.0-subtractor, 3)
        xs.append(round(build.time/60.0-subtractor, 3))
        datapoint['y_var'] = build.level
        ys.append(build.level)
        winningness = 'Win' if \
            build.player_match_summary.is_win \
            else 'Loss'
        if division == 'Player win/loss':
            datapoint['group_var'] = "{p}, ({win})".format(
                p=build.player_match_summary.player.display_name,
                win=winningness)
        elif division == 'Players':
            datapoint['group_var'] = "{p}".format(
                p=build.player_match_summary.player.display_name)
        elif division == 'Win/loss':
            datapoint['group_var'] = "{win}".format(
                win=winningness)
        datapoint['series_var'] = build.player_match_summary.match.steam_id
        datapoint['label'] = build.player_match_summary.player.display_name
        datapoint['split_var'] = 'Skill Progression'
        hero_id = build.player_match_summary.hero.steam_id
        if hero_classes[hero_id] is not None:
            datapoint['classes'].extend(hero_classes[hero_id])

        datalist.append(datapoint)

    params = params_dict()
    params['chart'] = 'scatterseries'
    params['x_min'] = 0
    params['x_max'] = max(xs)
    params['y_min'] = min(ys)
    params['y_max'] = max(ys)
    params['x_label'] = 'Time (m)'
    params['y_label'] = 'Level'

    return (datalist, params)


@do_profile()
def player_versus_winrate_json(
        player_id_1,
        player_id_2,
        game_mode_list=None,
        min_date=datetime.date(2009, 1, 1),
        max_date=None,
        group_var='alignment',
        plot_var='winrate',
        ):
    if max_date is None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    min_dt_utc = mktime(min_date.timetuple())

    hero_classes = hero_classes_dict()

    if min_dt_utc > max_date_utc:
        raise NoDataFound
    if game_mode_list is None:
        game_mode_list = [
            gm.steam_id
            for gm in GameMode.objects.filter(is_competitive=True)
        ]

    try:
        player_1 = Player.objects.get(steam_id=player_id_1)
        player_2 = Player.objects.get(steam_id=player_id_2)

    except Player.DoesNotExist:
        raise NoDataFound

    pmses = PlayerMatchSummary.objects.filter(
        player__in=[player_1, player_2],
        match__validity=Match.LEGIT,
        match__start_time__gte=min_dt_utc,
        match__start_time__lte=max_date_utc,
        match__game_mode__steam_id__in=game_mode_list,
    ).select_related().distinct()

    if len(pmses) == 0:
        raise NoDataFound

    pairings = {}
    for pms in pmses:
        if pms.hero.name not in pairings:
            pairings[pms.hero.name] = {
                player_1: {'wins': 0, 'losses': 0},
                player_2: {'wins': 0, 'losses': 0},
            }
        if pms.is_win:
            pairings[pms.hero.name][pms.player]['wins'] += 1
        else:
            pairings[pms.hero.name][pms.player]['losses'] += 1

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

    all_heroes = Hero.objects.filter(visible=True).values(
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

    data_list, groups = [], []
    for hero_name, dataset in pairings.iteritems():
        datadict = datapoint_dict()
        if group_var == 'hero':
            group = hero_info_dict[hero_name]['name']
        elif group_var == 'alignment':
            group = hero_info_dict[hero_name]['alignment'].title()
        groups.append(group)

        datadict.update({
            'group_var': group,
            'split_var': '',
            'label': hero_info_dict[hero_name]['name'],
            'tooltip': hero_info_dict[hero_name]['name'],
            'classes': [],
        })
        if hero_classes[hero_info_dict[hero_name]['steam_id']] is not None:
            datadict['classes'].extend(hero_classes[hero_info_dict[
                hero_name]['steam_id']
                ])
        datadict['point_size'] = min(
            dataset[player_1]['total_games'],
            dataset[player_2]['total_games']
            )
        datadict['stroke_width'] = 2
        if plot_var == 'winrate':

            datadict['x_var'] = dataset[player_1]['winrate']
            datadict['y_var'] = dataset[player_2]['winrate']
        else:
            datadict['x_var'] = dataset[player_1]['total_games']
            datadict['y_var'] = dataset[player_2]['total_games']

        data_list.append(datadict)

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in data_list])
    params['x_max'] = max([d['x_var'] for d in data_list])
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = max([d['y_var'] for d in data_list])
    params['groups'] = [d['group_var'] for d in data_list]
    params['x_label'] = "{name} {pvar}".format(
        name=player_1.display_name,
        pvar=plot_var,
    )
    params['y_label'] = "{name} {pvar}".format(
        name=player_2.display_name,
        pvar=plot_var,
    )
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['legendWidthPercent'] = .7
    params['legendHeightPercent'] = .1
    params['pointDomainMin'] = 0
    params['pointDomainMax'] = 10
    params['pointSizeMin'] = 2
    params['pointSizeMax'] = 5
    params['strokeSizeMin'] = 1
    params['strokeSizeMax'] = 1

    if plot_var == 'winrate':
        params['y_max'] = 100
        params['x_max'] = 100
        params['strokeDomainMin'] = 0
        params['strokeDomainMax'] = 1
    if group_var == 'hero':
        params['draw_legend'] = False
    elif group_var == 'alignment':
        params['draw_legend'] = True
    params = color_scale_params(params, groups)

    return (data_list, params)


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

    min_dt_utc = mktime(min_date.timetuple())

    if min_dt_utc > max_date_utc:
        raise NoDataFound

    all_heroes = Hero.objects.all()
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
        start_time__gte=min_dt_utc,
        start_time__lte=max_date_utc,
        game_mode__steam_id__in=game_modes,
        playermatchsummary__player_slot__lt=6,
    ).distinct()

    player_dire_matches = Match.objects.filter(
        playermatchsummary__player=player,
        validity=Match.LEGIT,
        start_time__gte=min_dt_utc,
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
    data_list, groups = [], []
    for name, dataset in outcome_dict.iteritems():
        hero = hero_names[name]
        datadict = datapoint_dict()
        if group_var == 'hero':
            group = hero.name.title()
        elif group_var == 'alignment':
            try:
                group = hero.herodossier.alignment.title()
            except HeroDossier.DoesNotExist:
                group = ''
        groups.append(group)

        datadict.update({
            'group_var': group,
            'split_var': '',
            'label': hero.name,
            'tooltip': hero.name,
            'classes': [],
        })
        if hero_classes[hero.steam_id] is not None:
            datadict['classes'].extend(hero_classes[hero.steam_id])

        if plot_var == 'winrate':
            datadict['point_size'] = dataset['same_side']['total_games']
            datadict['stroke_width'] = dataset['opposite_side']['total_games']

            datadict['x_var'] = dataset['same_side']['winrate']
            datadict['y_var'] = dataset['opposite_side']['winrate']
        else:
            datadict['point_size'] = \
                (dataset['same_side']['total_games']
                    + dataset['opposite_side']['total_games'])/2.0
            datadict['x_var'] = dataset['same_side']['total_games']
            datadict['y_var'] = dataset['opposite_side']['total_games']

        data_list.append(datadict)

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in data_list])
    params['x_max'] = max([d['x_var'] for d in data_list])
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = max([d['y_var'] for d in data_list])
    params['x_label'] = "Same-side {pvar}".format(
        pvar=plot_var,
    )
    params['y_label'] = "Opposite-side {pvar}".format(
        pvar=plot_var,
    )
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 35
    params['legendWidthPercent'] = .7
    params['legendHeightPercent'] = .1
    params['pointDomainMin'] = 0
    params['pointDomainMax'] = 10
    params['pointSizeMin'] = 1
    params['pointSizeMax'] = 5

    if plot_var == 'winrate':
        params['y_min'] = 0
        params['x_min'] = 0
        params['y_max'] = 100
        params['x_max'] = 100
        params['strokeDomainMin'] = 0
        params['strokeDomainMax'] = 10
        params['strokeSizeMin'] = 0
        params['strokeSizeMax'] = 2
    if group_var == 'hero':
        params['draw_legend'] = False
    elif group_var == 'alignment':
        params['draw_legend'] = True
    params = color_scale_params(params, [d['group_var'] for d in data_list])

    return (data_list, params)


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

    data_list = []
    params = params_dict()
    for role, info in role_dict.iteritems():

        if plot_var == 'performance':
            for player_id, data in info.iteritems():
                datadict = datapoint_dict()
                datadict.update({
                    'group_var': player_id,
                    'split_var': '',
                    'label': role,
                    'tooltip': role,
                    'x_var': data['games'],
                    'y_var': data['winrate'],
                    'classes': [slugify(role)],
                })
                x_label = "Games"
                y_label = "Winrate"

        elif plot_var == 'games':
                datadict = datapoint_dict()
                datadict.update({
                    'group_var': role,
                    'split_var': '',
                    'label': role,
                    'tooltip': role,
                    'x_var': info[player_1]['games'],
                    'y_var': info[player_2]['games'],
                    'classes': [slugify(role)],
                })
                x_label = "{p} Games".format(p=p1_obj.display_name)
                y_label = "{p} Games".format(p=p2_obj.display_name)

        elif plot_var == 'winrate':
                datadict = datapoint_dict()
                datadict.update({
                    'group_var': role,
                    'split_var': '',
                    'label': role,
                    'tooltip': role,
                    'x_var': info[player_1]['winrate'],
                    'y_var': info[player_2]['winrate'],
                    'classes': [slugify(role)],
                })
                datadict['classes'].append(slugify(role))
                x_label = "{p} Winrate".format(p=p1_obj.display_name)
                y_label = "{p} Winrate".format(p=p2_obj.display_name)
        data_list.append(datadict)

    params['x_min'] = min([d['x_var'] for d in data_list])
    params['x_max'] = max([d['x_var'] for d in data_list])
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = max([d['y_var'] for d in data_list])
    params['x_label'] = x_label
    params['y_label'] = y_label
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['legendWidthPercent'] = .7
    params['legendHeightPercent'] = .1
    params = color_scale_params(params, [d['group_var'] for d in data_list])

    return (data_list, params)
