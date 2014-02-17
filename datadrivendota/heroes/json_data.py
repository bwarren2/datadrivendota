import json
import operator

from itertools import chain
from django.conf import settings
from heroes.models import HeroDossier, Hero, invalid_option
from matches.models import PlayerMatchSummary,  Match, fetch_match_attributes
from utils.exceptions import NoDataFound
from utils.file_management import outsourceJson
from utils.charts import datapoint_dict, params_dict


def hero_vitals_json(hero_list, stats_list):
    # Currently, we are violating DRY with the available field listing from
    # the form and the R space being in different places and requiring that
    # they are the same.

    selected_hero_dossiers = HeroDossier.objects.filter(
        hero__steam_id__in=hero_list
    )

    if len(selected_hero_dossiers) == 0 or invalid_option(stats_list):
        raise NoDataFound
    datalist = []
    xs = []
    ys = []
    for hero_dossier in selected_hero_dossiers:
        for stat in stats_list:
            for level in range(1, 26):
                datadict = datapoint_dict()
                datadict.update({
                    'x_var': level,
                    'y_var': hero_dossier.level_stat(stat, level),
                    'group_var': hero_dossier.hero.name,
                    'label': hero_dossier.hero.name,
                    'split_var': stat,
                })
                datalist.append(datadict)
                xs.append(level)
                ys.append(hero_dossier.level_stat(stat, level))

    params = params_dict()
    params['x_min'] = min(xs)
    params['x_max'] = max(xs)
    params['y_min'] = min(ys)
    params['y_max'] = max(ys)
    params['x_label'] = 'Level'
    params['y_label'] = 'Quantity'
    params['draw_path'] = True
    params['chart'] = 'xyplot'
    params['outerWidth'] = 300
    params['outerHeight'] = 300

    return outsourceJson(datalist, params)


def hero_lineup_json(heroes, stat, level):
    # Database pulls and format python objects to go to R
    hero_dossiers = HeroDossier.objects.filter(
        hero__visible=True
    ).select_related()
    selected_names = [h.name for h in Hero.objects.filter(steam_id__in=heroes)]
    # @todo: An idiomatic way of doing this would be "if not len(foo)"
    # It's hard to explain when and why I would use "not" followed by an
    # expression that evaluates to zero, and when I would use "== 0". But for
    # lists, it's that you don't care about the length of the list as such,
    # it's that you care about whether it "meaningfully exists"
    # --kit 2014-02-16
    if len(hero_dossiers) == 0:
        raise NoDataFound

    try:
        hero_value = dict(
            (dossier.hero.safe_name(), dossier.fetch_value(stat, level))
            for dossier in hero_dossiers
        )
    except AttributeError:
        raise NoDataFound
    datalist = []
    ys = []
    xs = []

    hero_value = sorted(
        hero_value.iteritems(),
        key=operator.itemgetter(1),
        reverse=True
    )

    for key, val in hero_value:
        datadict = datapoint_dict()
        datadict['x_var'] = key
        datadict['y_var'] = val
        datadict['label'] = key
        datadict['tooltip'] = key
        datadict['group_var'] = key if key in selected_names else 'Else'
        datadict['split_var'] = 'Hero {stat}'.format(stat=stat)
        datalist.append(datadict)
        ys.append(val)
        xs.append(key)
    params = params_dict()
    params['y_min'] = 0
    params['y_max'] = max(ys)
    params['x_label'] = 'Hero'
    params['y_label'] = stat
    params['chart'] = 'barplot'
    params['outerWidth'] = 800
    params['outerHeight'] = 500
    params['x_set'] = xs
    params['padding']['bottom'] = 120
    params['tickValues'] = [x for ind, x in enumerate(xs) if ind % 2 == 0]
    return outsourceJson(datalist, params)


def hero_performance_json(
        hero,
        player,
        game_mode_list,
        x_var,
        y_var,
        group_var,
        split_var
        ):
    # Database pulls and format python objects to go to R
    matches = PlayerMatchSummary.objects.filter(
        match__game_mode__in=game_mode_list
    )
    # Ignore <10 min games
    matches = matches.filter(match__duration__gte=settings.MIN_MATCH_LENGTH)
    matches = matches.filter(hero__steam_id=hero, match__validity=Match.LEGIT)
    skill1 = matches.filter(match__skill=1).select_related()[:100]
    skill2 = matches.filter(match__skill=2).select_related()[:100]
    skill3 = matches.filter(match__skill=3).select_related()[:100]
    for game in chain(skill1, skill2, skill3):
        game.skill_level = game.match.skill

    if player is not None:
        player_games = matches.filter(player__steam_id=player).select_related()
        for game in player_games:
            game.skill_level = 'Player'
        match_pool = list(chain(skill1, skill2, skill3, player_games))
    else:
        match_pool = list(chain(skill1, skill2, skill3))

    if len(match_pool) == 0:
        raise NoDataFound

    try:
        x_vector_list, xlab = fetch_match_attributes(match_pool, x_var)
        y_vector_list, ylab = fetch_match_attributes(match_pool, y_var)
        match_list = fetch_match_attributes(match_pool, 'match_id')[0]
        if split_var is None:
            split_vector_list = ['No Split']
            split_lab = 'No Split'
        else:
            split_vector_list, split_lab = fetch_match_attributes(
                match_pool,
                split_var
            )
        if group_var is None:
            group_vector_list = ['No Grouping'] * len(x_vector_list)
            grouplab = 'No Grouping'
        else:
            group_vector_list, grouplab = fetch_match_attributes(
                match_pool,
                group_var
            )
    except AttributeError:
        raise NoDataFound

    return_json = json.dumps({
        'x_var': x_vector_list,
        'y_var': y_vector_list,
        'group_var': group_vector_list,
        'split_var': split_vector_list,
        'match_id': match_list,
        })
    return return_json, xlab, ylab, grouplab, split_lab
