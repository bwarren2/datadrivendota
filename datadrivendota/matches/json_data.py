from django.core.urlresolvers import reverse
from itertools import chain
from matches.models import (
    PlayerMatchSummary,
    Match,
    fetch_match_attributes,
    fetch_single_attribute,
    fetch_attribute_label,
    fetch_pms_attribute,
    SkillBuild
)
from utils.exceptions import NoDataFound
from utils.file_management import outsourceJson
from utils.charts import params_dict, datapoint_dict


def player_endgame_json(
        player_list,
        mode_list,
        x_var,
        y_var,
        split_var,
        group_var
        ):

    selected_summaries = PlayerMatchSummary.objects.filter(
        player__steam_id__in=player_list,
        match__game_mode__steam_id__in=mode_list,
        match__validity=Match.LEGIT)
    selected_summaries = selected_summaries.select_related()
    if len(selected_summaries) == 0:
        raise NoDataFound
    try:
        x_vector_list, xlab = fetch_match_attributes(selected_summaries, x_var)
        y_vector_list, ylab = fetch_match_attributes(selected_summaries, y_var)
        split_vector_list, split_lab = fetch_match_attributes(
            selected_summaries,
            split_var
        )
        group_vector_list, grouplab = fetch_match_attributes(
            selected_summaries,
            group_var
        )
        match_list = fetch_match_attributes(selected_summaries, 'match_id')[0]
    except AttributeError:
        raise NoDataFound

    datalist = []
    for key in range(0, len(x_vector_list)):
        datadict = datapoint_dict()
        datadict.update({
            'x_var': x_vector_list[key],
            'y_var': y_vector_list[key],
            'label': group_vector_list[key],
            'tooltip': match_list[key],
            'split_var': split_vector_list[key],
            'group_var': group_vector_list[key],
        })
        datalist.append(datadict)
    params = params_dict()
    params['x_min'] = min(x_vector_list)
    params['x_max'] = max(x_vector_list)
    params['y_min'] = min(y_vector_list)
    params['y_max'] = max(y_vector_list)
    params['x_label'] = xlab
    params['y_label'] = ylab
    params['chart'] = 'xyplot'

    return outsourceJson(datalist, params)


def team_endgame_json(
        player_list,
        mode_list,
        x_var,
        y_var,
        split_var,
        group_var,
        compressor
        ):

    # @todo: test this function? These appear to be the same query sets.
    # --kit 2012-02-16
    radiant_matches = Match.objects.filter(
        game_mode__steam_id__in=mode_list,
        validity=Match.LEGIT
    )
    dire_matches = Match.objects.filter(
        game_mode__steam_id__in=mode_list,
        validity=Match.LEGIT
    )
    for player in player_list:
        radiant_matches = radiant_matches.filter(
            playermatchsummary__player__steam_id=player,
            playermatchsummary__player_slot__lte=5
        )
        dire_matches = dire_matches.filter(
            playermatchsummary__player__steam_id=player,
            playermatchsummary__player_slot__gt=5
        )

    if len(radiant_matches) + len(dire_matches) == 0:
        raise NoDataFound
    radiant = PlayerMatchSummary.objects.filter(
        match__in=radiant_matches,
        player_slot__lte=5
    ).select_related()
    dire = PlayerMatchSummary.objects.filter(
        match__in=dire_matches,
        player_slot__gte=5
    ).select_related()

    pmses = list(chain(radiant, dire))
    x_data = dict([(p.match.steam_id, 0) for p in pmses])
    y_data = dict([(p.match.steam_id, 0) for p in pmses])
    group_data = dict([(p.match.steam_id, False) for p in pmses])
    split_data = dict([(p.match.steam_id, False) for p in pmses])

    for p in pmses:
        x_data[p.match.steam_id] += fetch_single_attribute(
            summary=p,
            attribute=x_var,
            compressor=compressor
        )
        y_data[p.match.steam_id] += fetch_single_attribute(
            summary=p,
            attribute=y_var,
            compressor=compressor
        )
        group_data[p.match.steam_id] = fetch_single_attribute(
            summary=p,
            attribute=group_var,
            compressor=compressor
        )
        split_data[p.match.steam_id] = fetch_single_attribute(
            summary=p,
            attribute=split_var,
            compressor=compressor
        )

    try:
        datalist = []
        for p in pmses:
            match_id = p.match.steam_id
            datadict = datapoint_dict()

            datadict.update({
                'x_var': x_data[match_id],
                'y_var': y_data[match_id],
                'group_var': group_data[match_id],
                'split_var': split_data[match_id],
                'label': group_data[match_id],
                'tooltip': match_id,
                'url': reverse(
                    'matches:match_detail',
                    kwargs={'match_id': match_id}
                ),
            })

            datalist.append(datadict)
            xlab = fetch_attribute_label(attribute=x_var)
            ylab = fetch_attribute_label(attribute=y_var) + " ({})".format(
                compressor
            )
    except AttributeError:
        raise NoDataFound

    params = params_dict()
    params['x_min'] = min(x_data.itervalues())
    params['x_max'] = max(x_data.itervalues())
    params['y_min'] = min(y_data.itervalues())
    params['y_max'] = max(y_data.itervalues())
    params['x_label'] = xlab
    params['y_label'] = ylab
    params['chart'] = 'xyplot'

    return outsourceJson(datalist, params)


def match_ability_json(match_id, split_var='No Split'):

    skill_builds = SkillBuild.objects.filter(
        player_match_summary__match__steam_id=match_id
    ).select_related().order_by('player_match_summary', 'level')
    datalist = []
    for build in skill_builds:

        side = build.player_match_summary.which_side()
        hero = build.player_match_summary.hero.name
        if split_var == 'No Split':
            split_param = 'No Split'
        elif split_var == 'hero':
            split_param = hero+'_foo'
        elif split_var == 'side':
            split_param = side

        datadict = datapoint_dict()
        minidict = {
            'x_var': build.time / 60,
            'y_var': build.level,
            'label': hero,
            'tooltip': build.ability.name,
            'split_var': split_param,
            'group_var': hero,
        }
        datadict.update(minidict)
        print minidict, datadict
        datalist.append(datadict)
    xs = [build.time/60 for build in skill_builds]
    ys = [build.level for build in skill_builds]
    
    params = params_dict()
    params['x_min'] = min(xs)
    params['x_max'] = max(xs)
    params['y_min'] = min(ys)
    params['y_max'] = max(ys)
    params['x_label'] = 'Time (m)'
    params['y_label'] = 'Level'
    params['draw_path'] = True
    params['chart'] = 'xyplot'

    return outsourceJson(datalist, params)


def match_parameter_json(match_id, x_var, y_var):
    pmses = PlayerMatchSummary.objects.filter(match__steam_id=match_id)
    data_list = []
    for pms in pmses:
        datadict = datapoint_dict()

        datadict.update({
            'x_var': fetch_pms_attribute(pms, x_var),
            'y_var': fetch_pms_attribute(pms, y_var),
            'group_var': fetch_pms_attribute(pms, 'which_side'),
            'split_var': '',
            'label': fetch_pms_attribute(pms, 'hero_name'),
            'tooltip': fetch_pms_attribute(pms, 'hero_name'),
        })
        data_list.append(datadict)

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in data_list])
    params['x_max'] = max([d['x_var'] for d in data_list])
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = max([d['y_var'] for d in data_list])
    params['x_label'] = fetch_attribute_label(x_var)
    params['y_label'] = fetch_attribute_label(y_var)
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 60
    params['outerWidth'] = 250
    params['outerHeight'] = 250

    return outsourceJson(data_list, params)
