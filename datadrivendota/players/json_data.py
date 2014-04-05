import datetime
from urllib import urlencode
from time import mktime
from django.db.models import Count
from matches.models import PlayerMatchSummary, GameMode, Match
from .models import Player
from utils.exceptions import NoDataFound
from utils.file_management import outsourceJson
from itertools import chain
from utils.charts import params_dict, datapoint_dict, color_scale_params
from heroes.models import Hero, Role
from matches.models import SkillBuild
from collections import defaultdict


def player_winrate_json(
        player_id,
        game_mode_list=None,
        role_list=[],
        min_date=datetime.date(2009, 1, 1),
        max_date=None,
        group_var='alignment',
        width=500,
        height=500
        ):
    if max_date is None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    min_dt_utc = mktime(min_date.timetuple())

    if role_list == []:
        roles = Role.objects.all()
    else:
        roles = Role.objects.filter(name__in=role_list)

    if min_dt_utc > max_date_utc:
        raise NoDataFound
    if game_mode_list is None:
        game_mode_list = [
            gm.steam_id
            for gm in GameMode.objects.filter(is_competitive=True)
        ]

    try:
        player = Player.objects.get(steam_id=player_id)
    except Player.DoesNotExist:
        raise NoDataFound
    annotations = PlayerMatchSummary.objects.filter(
        player=player,
        match__validity=Match.LEGIT,
        hero__roles__in=roles,
        match__game_mode__steam_id__in=game_mode_list,
    ).values('hero__name', 'is_win').annotate(Count('is_win'))

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

    all_heroes = Hero.objects.all().select_related()
    a = all_heroes
    data_list, groups = [], []
    for hero in heroes:
        datadict = datapoint_dict()
        hero_obj = all_heroes.get(name=hero)
        if group_var == 'hero':
            group = hero_obj.name.title()
        elif group_var == 'alignment':
            group = hero_obj.herodossier.alignment.title()
        groups.append(group)

        url_str = '/heroes/skill_progression/?game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&division=Skill&{extras}'.format(extras=urlencode({'hero': hero_obj.name,
            'player': player.display_name()}))

        datadict.update({
            'x_var': games[hero],
            'y_var': round(win_rates[hero], 2),
            'group_var': group,
            'split_var': '',
            'url': url_str,
            'label': hero,
            'tooltip': hero,
            'classes': [group, hero],
        })
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
    params['outerWidth'] = width
    params['outerHeight'] = height
    params['legendWidthPercent'] = .7
    params['legendHeightPercent'] = .7
    if group_var == 'hero':
        params['draw_legend'] = False
        group = []
    elif group_var == 'alignment':
        group = hero_obj.herodossier.alignment
        params['draw_legend'] = True
    params = color_scale_params(params, groups)

    return (data_list, params)


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
                p=build.player_match_summary.player.display_name(),
                win=winningness)
        elif division == 'Players':
            datapoint['group_var'] = "{p}".format(
                p=build.player_match_summary.player.display_name())
        elif division == 'Win/loss':
            datapoint['group_var'] = "{win}".format(
                win=winningness)
        datapoint['series_var'] = build.player_match_summary.match.steam_id
        datapoint['label'] = build.player_match_summary.player.display_name()
        datapoint['split_var'] = 'Skill Progression'
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


def player_versus_winrate_json(
        player_id_1,
        player_id_2,
        game_mode_list=None,
        role_list=[],
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

    if role_list == []:
        roles = Role.objects.all()
    else:
        roles = Role.objects.filter(name__in=role_list)

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
        match__game_mode__steam_id__in=game_mode_list,
    ).select_related().distinct()

    if len(pmses) == 0:
        raise NoDataFound

    pairings = {}
    for pms in pmses:
        if pms.hero not in pairings:
            pairings[pms.hero] = {
                player_1: {'wins': 0, 'losses': 0},
                player_2: {'wins': 0, 'losses': 0},
            }
        if pms.is_win:
            pairings[pms.hero][pms.player]['wins'] += 1
        else:
            pairings[pms.hero][pms.player]['losses'] += 1

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

    data_list, groups = [], []
    for hero, dataset in pairings.iteritems():
        datadict = datapoint_dict()
        if group_var == 'hero':
            group = hero.name.title()
        elif group_var == 'alignment':
            group = hero.herodossier.alignment.title()
        groups.append(group)

        datadict.update({
            'group_var': group,
            'split_var': '',
            'label': hero.name,
            'tooltip': hero.name,
            'classes': [hero.name, group],
        })
        if plot_var == 'winrate':
            datadict['point_size'] = dataset[player_1]['total_games']
            datadict['stroke_width'] = dataset[player_2]['total_games']

            datadict['x_var'] = dataset[player_1]['winrate']
            datadict['y_var'] = dataset[player_2]['winrate']
        else:
            datadict['point_size'] = \
                (dataset[player_1]['total_games'] \
                + dataset[player_2]['total_games'])/2.0
            datadict['x_var'] = dataset[player_1]['total_games']
            datadict['y_var'] = dataset[player_2]['total_games']

        data_list.append(datadict)

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in data_list])
    params['x_max'] = max([d['x_var'] for d in data_list])
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = max([d['y_var'] for d in data_list])
    params['x_label'] = "{name} {pvar}".format(
        name=player_1.persona_name,
        pvar=plot_var,
    )
    params['y_label'] = "{name} {pvar}".format(
        name=player_2.persona_name,
        pvar=plot_var,
    )
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['legendWidthPercent'] = .7
    params['legendHeightPercent'] = .1
    params['pointDomainMin'] = 0
    params['pointDomainMax'] = 10
    params['pointSizeMin'] = 1
    params['pointSizeMax'] = 5

    if plot_var == 'winrate':
        params['y_max'] = 100
        params['x_max'] = 100
        params['strokeDomainMin'] = 0
        params['strokeDomainMax'] = 10
        params['strokeSizeMin'] = 0
        params['strokeSizeMax'] = 2
    if group_var == 'hero':
        params['draw_legend'] = False
        group = []
    elif group_var == 'alignment':
        group = hero.herodossier.alignment
        params['draw_legend'] = True
    params = color_scale_params(params, groups)

    return (data_list, params)


def player_hero_side_json(
        player_id,
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

    if min_dt_utc > max_date_utc:
        raise NoDataFound
    if game_mode_list is None:
        game_mode_list = [
            gm.steam_id
            for gm in GameMode.objects.filter(is_competitive=True)
        ]

    try:
        player = Player.objects.get(steam_id=player_id)

    except Player.DoesNotExist:
        raise NoDataFound

    def side_match(pms_set, outcome_dict, given_side):
        for pms in pms_set:
            if pms.hero not in outcome_dict:
                outcome_dict[pms.hero] = {
                    'same_side': {
                        'wins': 0,
                        'losses': 0,
                    },
                    'opposite_side': {
                        'wins': 0,
                        'losses': 0,
                    }
                }
            if pms.is_win:
                cat = 'wins'
            else:
                cat = 'losses'
            if pms.which_side() == given_side:
                side = 'same_side'
            else:
                side = 'opposite_side'
            outcome_dict[pms.hero][side][cat] += 1

    player_radiant_matches = Match.objects.filter(
        playermatchsummary__player=player,
        validity=Match.LEGIT,
        game_mode__steam_id__in=game_mode_list,
        playermatchsummary__player_slot__lte=6,
    ).distinct()

    pmses = PlayerMatchSummary.objects.filter(
        match__in=player_radiant_matches,
        ).exclude(
        player=player).select_related()

    outcome_dict = {}
    side_match(pmses, outcome_dict, 'Radiant')

    player_dire_matches = Match.objects.filter(
        playermatchsummary__player=player,
        validity=Match.LEGIT,
        game_mode__steam_id__in=game_mode_list,
        playermatchsummary__player_slot__gte=6,
    ).distinct()

    pmses = PlayerMatchSummary.objects.filter(
        match__in=player_dire_matches,
        ).exclude(
        player=player).select_related()

    side_match(pmses, outcome_dict, 'Dire')

    for dct in outcome_dict.itervalues():
        for side in dct.itervalues():
            side['total_games'] = side['wins']+side['losses']
            divisor = 1 if side['total_games'] == 0 else side['total_games']
            side['winrate'] = side['wins']/float(divisor)*100.0

    data_list, groups = [], []
    for hero, dataset in outcome_dict.iteritems():
        datadict = datapoint_dict()
        if group_var == 'hero':
            group = hero.name.title()
        elif group_var == 'alignment':
            group = hero.herodossier.alignment.title()
        groups.append(group)

        datadict.update({
            'group_var': group,
            'split_var': '',
            'label': hero.name,
            'tooltip': hero.name,
            'classes': [hero.name, group],
        })
        if plot_var == 'winrate':
            datadict['point_size'] = dataset['same_side']['total_games']
            datadict['stroke_width'] = dataset['opposite_side']['total_games']

            datadict['x_var'] = dataset['same_side']['winrate']
            datadict['y_var'] = dataset['opposite_side']['winrate']
        else:
            datadict['point_size'] = \
                (dataset['same_side']['total_games'] \
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
    params['margin']['left'] = 12*len(str(params['y_max']))
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
        group = []
    elif group_var == 'alignment':
        group = hero.herodossier.alignment
        params['draw_legend'] = True
    params = color_scale_params(params, groups)

    return (data_list, params)
