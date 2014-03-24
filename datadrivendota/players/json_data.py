import datetime
from time import mktime
from django.db.models import Count
from matches.models import PlayerMatchSummary, GameMode, Match
from .models import Player
from utils.exceptions import NoDataFound
from utils.file_management import outsourceJson
from itertools import chain
from utils.charts import params_dict, datapoint_dict, color_scale_params
from heroes.models import Hero, Role, HeroDossier
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
    print role_list
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

    win_rates = {hero:
        float(wins.get(hero, 0))
        / (wins.get(hero, 0) + losses.get(hero, 0)) * 100
        for hero in heroes
    }
    games = {hero: wins.get(hero, 0) + losses.get(hero, 0) for hero in heroes}

    all_heroes = Hero.objects.all().select_related()
    data_list, groups = [], []
    for hero in heroes:
        datadict = datapoint_dict()
        hero_obj = all_heroes.filter(name=hero)
        if group_var == 'hero':
            group = hero_obj[0].name.title()
        elif group_var == 'alignment':
            group = hero_obj[0].herodossier.alignment.title()
        groups.append(group)
        datadict.update({
            'x_var': games[hero],
            'y_var': round(win_rates[hero], 2),
            'group_var': group,
            'split_var': '',
            'label': hero,
            'tooltip': hero,
        })
        data_list.append(datadict)

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in data_list])
    params['x_max'] = max([d['x_var'] for d in data_list])
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = max([d['y_var'] for d in data_list])
    params['x_label'] = 'Games'
    params['y_label'] = 'Winrate'
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['outerWidth'] = width
    params['outerHeight'] = height
    if group_var == 'hero':
        params['draw_legend'] = False
        group = hero_obj[0]
    elif group_var == 'alignment':
        group = hero_obj[0].herodossier.alignment
        params['draw_legend'] = True
    params = color_scale_params(params, groups)

    return outsourceJson(data_list, params)


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
                p=build.player_match_summary.player.persona_name,
                win=winningness)
        elif division == 'Players':
            datapoint['group_var'] = "{p}".format(
                p=build.player_match_summary.player.persona_name)
        elif division == 'Win/loss':
            datapoint['group_var'] = "{win}".format(
                win=winningness)
        datapoint['series_var'] = build.player_match_summary.match.steam_id
        datapoint['label'] = build.player_match_summary.player.persona_name
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

    foo = outsourceJson(datalist, params)
    return foo
