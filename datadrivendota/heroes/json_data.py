import json
import operator
from itertools import chain

from django.core.urlresolvers import reverse

from heroes.models import HeroDossier, Hero, invalid_option, Ability
from matches.models import (
    PlayerMatchSummary,
    Match,
    fetch_match_attributes,
    SkillBuild,
    skill_name
)
from players.models import Player
from django.db.models import Count

from utils.exceptions import NoDataFound
from utils.charts import (
    datapoint_dict,
    params_dict,
    color_scale_params,
    hero_classes_dict
    )


def hero_vitals_json(heroes, stats):
    # Currently, we are violating DRY with the available field listing from
    # the form and the R space being in different places and requiring that
    # they are the same.
    selected_hero_dossiers = HeroDossier.objects.filter(
        hero__steam_id__in=heroes
    )

    if len(selected_hero_dossiers) == 0 or invalid_option(stats):
        raise NoDataFound
    datalist, xs, ys, groups = [], [], [], []

    hero_classes = hero_classes_dict()

    for hero_dossier in selected_hero_dossiers:
        group = hero_dossier.hero.name
        groups.append(group)
        for stat in stats:
            for level in range(1, 26):
                datadict = datapoint_dict()
                datadict.update({
                    'x_var': level,
                    'y_var': hero_dossier.level_stat(stat, level),
                    'group_var': group,
                    'label': hero_dossier.hero.name,
                    'tooltip': "{hero}, {val}".format(
                        hero=hero_dossier.hero.name,
                        val=hero_dossier.level_stat(stat, level)
                    ),
                    'split_var': stat.title(),
                    'classes': [],
                })
                if hero_classes[hero_dossier.hero.steam_id] is not None:
                    datadict['classes'].extend(
                        hero_classes[hero_dossier.hero.steam_id]
                    )

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
    params = color_scale_params(params, groups)
    return (datalist, params)


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
            (dossier, dossier.fetch_value(stat, level))
            for dossier in hero_dossiers
        )
    except AttributeError:
        raise NoDataFound
    datalist, ys, xs, groups = [], [], [], []

    hero_value = sorted(
        hero_value.iteritems(),
        key=operator.itemgetter(1),
        reverse=True
    )
    hero_classes = hero_classes_dict()

    for key, val in hero_value:
        group = key.hero.safe_name() \
            if key.hero.safe_name() in selected_names \
            else key.alignment.title()
        groups.append(group)
        datadict = datapoint_dict()
        datadict['x_var'] = key.hero.safe_name()
        datadict['y_var'] = val
        datadict['label'] = key.hero.safe_name()
        datadict['tooltip'] = "{name} ({val})".format(
            name=key.hero.safe_name(),
            val=val,
        )
        datadict['group_var'] = group
        datadict['classes'] = []
        datadict['split_var'] = 'Hero {stat}'.format(stat=stat)

        if hero_classes[key.hero.steam_id] is not None:
            datadict['classes'].extend(
                hero_classes[key.hero.steam_id]
            )

        datalist.append(datadict)
        ys.append(val)
        xs.append(key.hero.safe_name())
    params = params_dict()
    params['y_min'] = 0
    params['y_max'] = max(ys)
    params['x_label'] = 'Hero'
    params['y_label'] = stat
    params['chart'] = 'barplot'
    params['outerWidth'] = 800
    params['outerHeight'] = 500
    params['x_set'] = xs
    params['legendWidthPercent'] = .7
    params['legendHeightPercent'] = .8
    params['padding']['bottom'] = 120
    params = color_scale_params(params, groups)

    params['tickValues'] = [x for ind, x in enumerate(xs) if ind % 2 == 0]
    return (datalist, params)


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


def hero_performance_chart_json(
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
        player_game_ids = fetch_match_attributes(player_games, 'match_id')[0]
    else:
        match_pool = list(chain(skill1, skill2, skill3))

    if len(match_pool) == 0:
        raise NoDataFound

    try:
        hero_classes = hero_classes_dict()
        x_vector_list, xlab = fetch_match_attributes(match_pool, x_var)
        y_vector_list, ylab = fetch_match_attributes(match_pool, y_var)
        match_list = fetch_match_attributes(match_pool, 'match_id')[0]
        hero_id_list, foo = fetch_match_attributes(match_pool, 'hero_steam_id')

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
        datalist = []
        grouplist = []
        for key in range(0, len(x_vector_list)):
            datadict = datapoint_dict()
            if group_var == 'skill_name':
                if match_list[key] in player_game_ids:
                    group_var_elt = 'Player'
                else:
                    group_var_elt = group_vector_list[key]
            else:
                group_var_elt = group_vector_list[key]
            grouplist.append(group_var_elt)
            datadict.update({
                'x_var': x_vector_list[key],
                'y_var': y_vector_list[key],
                'label': group_vector_list[key],
                'tooltip': match_list[key],
                'split_var': split_vector_list[key],
                'group_var': group_var_elt,
                'classes': [],
                'url': reverse(
                    'matches:match_detail',
                    kwargs={'match_id': match_list[key]}
                )

            })
            if hero_classes[hero_id_list[key]] is not None:
                datadict['classes'].extend(
                    hero_classes[hero_id_list[key]]
                )

            datalist.append(datadict)
    except AttributeError:
        raise NoDataFound

    params = params_dict()
    params['x_min'] = min(x_vector_list)
    params['x_max'] = max(x_vector_list)
    params['y_min'] = min(y_vector_list)
    params['y_max'] = max(y_vector_list)
    params['x_label'] = xlab
    params['y_label'] = ylab
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['chart'] = 'xyplot'
    if group_var == 'skill_name':
        grouplist = ['Low Skill', 'Medium Skill', 'High Skill']
        if player is not None:
            grouplist.append('Player')
    params = color_scale_params(params, grouplist)
    return (datalist, params)


def hero_progression_json(hero, player, game_modes, division):
    pmses = PlayerMatchSummary.objects.filter(
        match__game_mode__in=game_modes
    )

    pmses = pmses.filter(hero__steam_id=hero, match__validity=Match.LEGIT)
    skill1 = pmses.filter(match__skill=1).select_related()[:100]
    skill2 = pmses.filter(match__skill=2).select_related()[:100]
    skill3 = pmses.filter(match__skill=3).select_related()[:100]

    if player is not None:
        player_games = pmses.filter(player__steam_id=player).select_related()
        player_game_ids = [pg.id for pg in player_games]
        pmses_pool = list(chain(skill1, skill2, skill3, player_games))
    else:
        player_game_ids = []
        pmses_pool = list(chain(skill1, skill2, skill3))

    if len(pmses_pool) == 0:
        raise NoDataFound

    sbs = SkillBuild.objects.filter(
        player_match_summary__in=pmses_pool,
    ).select_related().order_by('player_match_summary', 'level')
    sbs = sbs.values(
        'level',
        'time',
        'player_match_summary__is_win',
        'player_match_summary__id',
        'player_match_summary__match__skill',
        'player_match_summary__match__steam_id',
        'player_match_summary__player__persona_name',
        'player_match_summary__hero__steam_id',
    )
    datalist, xs, ys, groups = [], [], [], []
    hero_classes = hero_classes_dict()
    for build in sbs:
        if build['level'] == 1:
            subtractor = build['time']/60.0

        datapoint = datapoint_dict()
        datapoint['x_var'] = round(build['time']/60.0-subtractor, 3)
        xs.append(round(build['time']/60.0-subtractor, 3))
        datapoint['y_var'] = build['level']
        ys.append(build['level'])

        winningness = 'Win' if \
            build['player_match_summary__is_win'] \
            else 'Loss'

        skill_value = skill_name(build['player_match_summary__match__skill'])\
            if build['player_match_summary__id'] not in player_game_ids \
            else 'Player'

        if division == 'Skill win/loss':
            group = "{s}, ({win})".format(
                s=skill_value,
                win=winningness)
        elif division == 'Skill':
            group = "{s}".format(
                s=skill_value)
        elif division == 'Win/loss':
            group = "{win}".format(
                win=winningness)

        datapoint['group_var'] = group
        groups.append(group)

        datapoint['series_var'] = build[
            'player_match_summary__match__steam_id'
        ]
        datapoint['label'] = build[
            'player_match_summary__player__persona_name'
        ]
        datapoint['split_var'] = 'Skill Progression'
        hero_id = build['player_match_summary__hero__steam_id']
        if hero_classes[hero_id] is not None:
            datapoint['classes'].extend(
                hero_classes[hero_id]
            )

        datalist.append(datapoint)

    params = params_dict()
    params['chart'] = 'scatterseries'
    params['x_min'] = 0
    params['x_max'] = max(xs)
    params['y_min'] = min(ys)
    params['y_max'] = max(ys)
    params['x_label'] = 'Time (m)'
    params['y_label'] = 'Level'
    params = color_scale_params(params, groups)

    return (datalist, params)


def hero_skillbuild_winrate_json(
    hero,
    player,
    game_modes,
    levels,
):
    datalist = []
    level_list = levels
    hero_id = hero
    player_id = player
    game_mode_list = game_modes

    ability_lst = Ability.objects.all().select_related()
    id_name_map = {ab.steam_id: ab.name for ab in ability_lst}

    def to_label(strng):
        choice_lst = strng.split("-")
        label = ""
        for choice in set(choice_lst):
            label += "{name} x{ct} <br>".format(
                name=id_name_map[int(choice)],
                ct=len([x for x in choice_lst if x == choice]),
                )
        return label

    for level in level_list:
        sbs = SkillBuild.objects.filter(
            player_match_summary__match__game_mode__in=game_mode_list,
            player_match_summary__hero__steam_id=hero_id,
            player_match_summary__player__steam_id=player_id,
            player_match_summary__level__gte=level,
            player_match_summary__match__validity=Match.LEGIT,
            level__lte=level
        ).select_related()

        match_wins = list(set([
            sb.player_match_summary.match.steam_id
            for sb in sbs if sb.player_match_summary.is_win
        ]))
        match_losses = list(set([
            sb.player_match_summary.match.steam_id
            for sb in sbs if not sb.player_match_summary.is_win
        ]))

        match_dict = {}
        for sb in sbs:
            match_id = sb.player_match_summary.match.steam_id
            ability_id = sb.ability.steam_id
            if match_id not in match_dict:
                match_dict[match_id] = []
            match_dict[match_id].append(ability_id)

        match_dict = {
            key: sorted(value) for key, value in match_dict.iteritems()
        }

        build_dict = {}

        def to_str(lst):
            return "-".join((str(id) for id in lst))

        mygen = (to_str(x) for x in match_dict.itervalues())

        dimensions = set(mygen)

        for id_str in dimensions:
            if id_str not in build_dict:
                build_dict[id_str] = {}
            build_dict[id_str]['games'] = len(
                [key for key in match_dict
                    if to_str(match_dict[key]) == id_str]
            )
            build_dict[id_str]['wins'] = len(
                [match_id for match_id in match_wins
                    if to_str(match_dict[match_id]) == id_str]
            )
            build_dict[id_str]['losses'] = len(
                [match_id for match_id in match_losses
                    if to_str(match_dict[match_id]) == id_str]
            )
            denominator = float(
                build_dict[id_str]['games']
                if build_dict[id_str]['games'] > 0 else 1
            )
            build_dict[id_str]['winrate'] = \
                build_dict[id_str]['wins'] / denominator*100

        for build, datadict in build_dict.iteritems():
            datapoint = datapoint_dict()
            datapoint['x_var'] = datadict['games']
            datapoint['y_var'] = datadict['winrate']
            datapoint['group_var'] = "By Level {lvl}".format(lvl=level)
            datapoint['label'] = to_label(build)
            datapoint['tooltip'] = to_label(build)
            datapoint['split_var'] = ''
            datalist.append(datapoint)

    params = params_dict()
    params['chart'] = 'xyplot'
    params['x_min'] = 0
    params['x_max'] = max([d['x_var'] for d in datalist])
    params['y_min'] = 0
    params['y_max'] = 100
    params['x_label'] = 'Games'
    params['y_label'] = 'Winrate'
    params = color_scale_params(params, [d['group_var'] for d in datalist])

    return (datalist, params)


def update_player_winrate(
    hero,
    game_modes,
):

    hero_obj = Hero.objects.get(steam_id=hero)
    p_games = Player.objects.filter(
        updated=True,
        playermatchsummary__hero__steam_id=hero,
        ).annotate(Count('playermatchsummary__id'))

    dict_games = {p: {'games': p.playermatchsummary__id__count}
                  for p in p_games}

    p_wins = Player.objects.filter(
        updated=True,
        playermatchsummary__hero__steam_id=hero,
        playermatchsummary__is_win=True,
        ).annotate(Count('playermatchsummary__id'))

    dict_wins = {p: p.playermatchsummary__id__count for p in p_wins}

    for p in dict_games.iterkeys():
        dict_games[p]['wins'] = dict_wins.get(p, 0)

    datalist = []
    for p, info in dict_games.iteritems():

        url_str = reverse(
            'players:hero_style',
            kwargs={
                'hero_name': hero_obj.machine_name,
                'player_id': p.steam_id,
            }
        )

        datapoint = datapoint_dict()
        datapoint['x_var'] = info['games']
        datapoint['y_var'] = info['wins']/float(info['games'])*100
        datapoint['group_var'] = 'Pro' if p.pro_name is not None else 'Player'
        datapoint['label'] = p.display_name
        datapoint['tooltip'] = p.display_name
        datapoint['url'] = url_str
        datapoint['split_var'] = 'Tracked Player Winrate'
        datalist.append(datapoint)

    params = params_dict()
    params['chart'] = 'xyplot'
    params['x_min'] = 0
    params['x_max'] = max([d['x_var'] for d in datalist])
    params['y_min'] = 0
    params['y_max'] = 100
    params['x_label'] = 'Games'
    params['y_label'] = 'Winrate'
    params = color_scale_params(params, [d['group_var'] for d in datalist])

    return (datalist, params)
