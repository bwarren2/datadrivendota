from math import floor
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Sum
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
from heroes.models import Assignment
from utils.exceptions import NoDataFound
from utils.charts import (
    params_dict,
    datapoint_dict,
    color_scale_params,
    hero_classes_dict
)
from players.models import Player

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
def player_team_endgame_json(
        players,
        game_modes,
        x_var,
        y_var,
        split_var,
        group_var,
        ):
    #Takes a player's games and gives the team's results.

    dictAttributes = {
        'kills': 'playermatchsummary__kills',
        'deaths': 'playermatchsummary__deaths',
        'assists': 'playermatchsummary__assists',
        'last_hits': 'playermatchsummary__last_hits',
        'denies': 'playermatchsummary__denies',
        'hero_damage': 'playermatchsummary__hero_damage',
        'tower_damage': 'playermatchsummary__tower_damage',
        'hero_healing': 'playermatchsummary__hero_healing',
        'level': 'playermatchsummary__level',
        'gold_total': 'playermatchsummary__gold_per_min',
        'xp_total': 'playermatchsummary__xp_per_min',
    }

    dictDerivedAttributes = {
        'K-D+.5*A': '',
        'first_blood_time': 'first_blood_time',
        'gold_total': 'playermatchsummary__gold_per_min',
        'xp_total': 'playermatchsummary__xp_per_min',
        'duration': 'duration',
    }

    def get_var(annotation, var, dictAttributes, dictDerivedAttributes):
        if var in dictDerivedAttributes:
            if var == 'K-D+.5*A':
                return annotation.playermatchsummary__kills__sum\
                    - annotation.playermatchsummary__deaths__sum\
                    + annotation.playermatchsummary__assists__sum/2.0
            if var == 'first_blood_time':
                return annotation.first_blood_time
            if var == 'gold_total':
                return annotation.duration/60.0\
                    * annotation.playermatchsummary__gold_per_min__sum
            if var == 'xp_total':
                return annotation.duration/60.0\
                    * annotation.playermatchsummary__xp_per_min__sum
            if var == 'duration':
                return annotation.duration/60.0
        if var in dictAttributes:
            return getattr(annotation, (dictAttributes[var])+'__sum')

    datalist = []
    player_obj_list = []
    for player in players:

        player_obj = Player.objects.get(steam_id=player)
        player_obj_list.append(player_obj)
        radiant_matches = Match.objects.filter(
            game_mode__steam_id__in=game_modes,
            playermatchsummary__player__steam_id=player,
            playermatchsummary__player_slot__lte=6,
            validity=Match.LEGIT)

        dire_matches = Match.objects.filter(
            game_mode__steam_id__in=game_modes,
            playermatchsummary__player__steam_id=player,
            playermatchsummary__player_slot__gte=6,
            validity=Match.LEGIT)

        radiant_annotations = Match.objects.filter(
            id__in=[m.id for m in radiant_matches],
            playermatchsummary__player_slot__lte=6)\
            .annotate(Sum('playermatchsummary__kills'))\
            .annotate(Sum('playermatchsummary__deaths'))\
            .annotate(Sum('playermatchsummary__assists'))\

        dire_annotations = Match.objects.filter(
            id__in=[m.id for m in dire_matches],
            playermatchsummary__player_slot__gte=6)\
            .annotate(Sum('playermatchsummary__kills'))\
            .annotate(Sum('playermatchsummary__deaths'))\
            .annotate(Sum('playermatchsummary__assists'))\


        if x_var in dictAttributes:
            dire_annotations = \
                dire_annotations.annotate(Sum(dictAttributes[x_var]))
            radiant_annotations = \
                radiant_annotations.annotate(Sum(dictAttributes[x_var]))
        if y_var in dictAttributes:
            dire_annotations = \
                dire_annotations.annotate(Sum(dictAttributes[y_var]))
            radiant_annotations = \
                radiant_annotations.annotate(Sum(dictAttributes[y_var]))

        pmses = PlayerMatchSummary.objects.filter(
            player__steam_id=player,
            match__game_mode__steam_id__in=game_modes,
            match__validity=Match.LEGIT,
            ).values(
            'hero__name',
            'hero__steam_id',
            'match__steam_id',
            'is_win',
            )
        mapping_dict = {
            d['match__steam_id']:
            {
                'hero': d['hero__name'],
                'is_win': d['is_win'],
                'hero_id': d['hero__steam_id']
            }
            for d in pmses
        }
        hero_classes = hero_classes_dict()

        datasection = [datapoint_dict()
                    for x in range(0, (
                        len(radiant_annotations)+len(dire_annotations))
                    )]
        for i, annotation in enumerate(chain(
            radiant_annotations,
            dire_annotations
        )):
            plot_x_var = get_var(
                annotation,
                x_var,
                dictAttributes,
                dictDerivedAttributes
                )
            plot_y_var = get_var(
                annotation,
                y_var,
                dictAttributes,
                dictDerivedAttributes
                )

            if split_var == 'No Split':
                split_param = 'No Split'
            elif split_var == 'game_mode':
                split_param = annotation.game_mode.description
            elif split_var == 'player':
                split_param = player_obj.display_name
            elif split_var == 'is_win':
                if mapping_dict[annotation.steam_id]['is_win']:
                    split_param = 'Won'
                else:
                    split_param = 'Lost'

            if group_var == 'No Split':
                group_param = 'No Split'
            elif group_var == 'game_mode':
                group_param = annotation.game_mode.description
            elif group_var == 'player':
                group_param = player_obj.display_name
            elif group_var == 'is_win':
                if mapping_dict[annotation.steam_id]['is_win']:
                    group_param = 'Won'
                else:
                    group_param = 'Lost'

            datadict = datasection[i]
            datadict.update({
                'x_var': plot_x_var,
                'y_var': plot_y_var,
                'label': annotation.steam_id,
                'tooltip': annotation.steam_id,
                'split_var': split_param,
                'group_var': group_param,
                'classes': [],
                'url': 'matches/{0}'.format(annotation.steam_id)
            })
            if hero_classes[
                    mapping_dict[annotation.steam_id]['hero_id']
            ] is not None:
                datadict['classes'].extend(
                    hero_classes[
                        mapping_dict[annotation.steam_id]['hero_id']
                        ]
                )

            datasection.append(datadict)
        datalist.extend(datasection)
    if len(datalist) == 0:
        raise NoDataFound

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in datalist])
    params['x_max'] = max([d['x_var'] for d in datalist])
    params['y_min'] = min([d['y_var'] for d in datalist])
    params['y_max'] = max([d['y_var'] for d in datalist])
    params['legendWidthPercent'] = .25
    if x_var == 'duration':
        params['x_label'] = 'Duration (m)'
    else:
        params['x_label'] = x_var.title()
    params['y_label'] = y_var.title()
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['chart'] = 'xyplot'
    params = color_scale_params(
        params,
        [p.display_name for p in player_obj_list]
    )
    return (datalist, params)


@do_profile()
def player_endgame_json(
        players,
        game_modes,
        x_var,
        y_var,
        split_var,
        group_var
        ):
    #Gives the player's endgame results

    selected_summaries = PlayerMatchSummary.objects.filter(
        player__steam_id__in=players,
        match__game_mode__steam_id__in=game_modes,
        match__validity=Match.LEGIT)
    selected_summaries = selected_summaries.select_related()

    if len(selected_summaries) == 0:
        raise NoDataFound

    hero_classes = hero_classes_dict()

    datalist = []
    for pms in selected_summaries:
        datadict = datapoint_dict()
        datadict.update({
            'x_var': fetch_pms_attribute(pms, x_var),
            'y_var': fetch_pms_attribute(pms, y_var),
            'label': fetch_pms_attribute(pms, group_var),
            'tooltip': fetch_pms_attribute(pms, 'match_id'),
            'group_var': fetch_pms_attribute(pms, group_var),
            'classes': [],
            'url': reverse(
                'matches:match_detail',
                kwargs={'match_id': fetch_pms_attribute(pms, 'match_id')}
            )

        })
        if split_var is None or split_var == 'No Split':
            datadict['split_var'] = '',
        else:
            datadict['split_var'] = fetch_pms_attribute(pms, split_var),
        if hero_classes[pms.hero.steam_id] is not None:
            datadict['classes'].extend(
                hero_classes[pms.hero.steam_id]
            )

        datalist.append(datadict)

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in datalist])
    params['x_max'] = max([d['x_var'] for d in datalist])
    params['y_min'] = min([d['y_var'] for d in datalist])
    params['y_max'] = max([d['y_var'] for d in datalist])
    params['x_label'] = x_var.title()
    params['y_label'] = y_var.title()
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['chart'] = 'xyplot'
    params = color_scale_params(params, [d['group_var'] for d in datalist])
    return (datalist, params)


@do_profile()
def team_endgame_json(
        players,
        game_modes,
        x_var,
        y_var,
        split_var,
        group_var,
        compressor
        ):
    """Gives the endgame results for any game where the given players were on the same team"""

    matches = Match.objects.filter(
        game_mode__steam_id__in=game_modes,
        validity=Match.LEGIT
    )
    for player in players:
        radiant_matches = matches.filter(
            playermatchsummary__player__steam_id=player,
            playermatchsummary__player_slot__lte=5
        )
        dire_matches = matches.filter(
            playermatchsummary__player__steam_id=player,
            playermatchsummary__player_slot__gt=5
        )

    if len(radiant_matches) + len(dire_matches) == 0:
        raise NoDataFound

    dictAttributes = {
        'kills': 'playermatchsummary__kills',
        'deaths': 'playermatchsummary__deaths',
        'assists': 'playermatchsummary__assists',
        'last_hits': 'playermatchsummary__last_hits',
        'denies': 'playermatchsummary__denies',
        'hero_damage': 'playermatchsummary__hero_damage',
        'tower_damage': 'playermatchsummary__tower_damage',
        'hero_healing': 'playermatchsummary__hero_healing',
        'level': 'playermatchsummary__level',
        'gold_total': 'playermatchsummary__gold_per_min',
        'xp_total': 'playermatchsummary__xp_per_min',
    }

    dictDerivedAttributes = {
        'K-D+.5*A': '',
        'first_blood_time': 'first_blood_time',
        'gold_total': 'playermatchsummary__gold_per_min',
        'xp_total': 'playermatchsummary__xp_per_min',
        'duration': 'duration',
    }

    def get_var(annotation, var, dictAttributes, dictDerivedAttributes):
        if var in dictDerivedAttributes:
            if var == 'K-D+.5*A':
                return annotation.playermatchsummary__kills__sum\
                    - annotation.playermatchsummary__deaths__sum\
                    + annotation.playermatchsummary__assists__sum/2.0
            if var == 'first_blood_time':
                return annotation.first_blood_time
            if var == 'gold_total':
                return annotation.duration/60.0\
                    * annotation.playermatchsummary__gold_per_min__sum
            if var == 'xp_total':
                return annotation.duration/60.0\
                    * annotation.playermatchsummary__xp_per_min__sum
            if var == 'duration':
                return annotation.duration/60.0
        if var in dictAttributes:
            return getattr(annotation, (dictAttributes[var])+'__sum')

    radiant_annotations = Match.objects.filter(
        id__in=[m.id for m in radiant_matches],
        playermatchsummary__player_slot__lte=6)\
        .annotate(Sum('playermatchsummary__kills'))\
        .annotate(Sum('playermatchsummary__deaths'))\
        .annotate(Sum('playermatchsummary__assists'))\

    dire_annotations = Match.objects.filter(
        id__in=[m.id for m in dire_matches],
        playermatchsummary__player_slot__gte=6)\
        .annotate(Sum('playermatchsummary__kills'))\
        .annotate(Sum('playermatchsummary__deaths'))\
        .annotate(Sum('playermatchsummary__assists'))\


    if x_var in dictAttributes:
        dire_annotations = \
            dire_annotations.annotate(Sum(dictAttributes[x_var]))
        radiant_annotations = \
            radiant_annotations.annotate(Sum(dictAttributes[x_var]))
    if y_var in dictAttributes:
        dire_annotations = \
            dire_annotations.annotate(Sum(dictAttributes[y_var]))
        radiant_annotations = \
            radiant_annotations.annotate(Sum(dictAttributes[y_var]))

    try:
        datalist = []
        for annotation in chain(radiant_annotations, dire_annotations):
            match_id = annotation.steam_id

            datadict = datapoint_dict()

            plot_x_var = get_var(
                annotation,
                x_var,
                dictAttributes,
                dictDerivedAttributes
                )
            plot_y_var = get_var(
                annotation,
                y_var,
                dictAttributes,
                dictDerivedAttributes
                )

            datadict.update({
                'x_var': plot_x_var,
                'y_var': plot_y_var,
                'group_var': False,
                'split_var': False,
                'label': match_id,
                'tooltip': match_id,
                'url': reverse(
                    'matches:match_detail',
                    kwargs={'match_id': match_id}
                ),
                'classes': [],

            })

            datalist.append(datadict)
            xlab = fetch_attribute_label(attribute=x_var)
            ylab = fetch_attribute_label(attribute=y_var)
    except AttributeError:
        raise NoDataFound
    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in datalist])
    params['x_max'] = max([d['x_var'] for d in datalist])
    params['y_min'] = min([d['y_var'] for d in datalist])
    params['y_max'] = max([d['y_var'] for d in datalist])
    params['x_label'] = xlab
    params['y_label'] = ylab
    params['chart'] = 'xyplot'
    params['margin']['left'] = 12*len(str(params['y_max']))
    groups = [False]
    params = color_scale_params(params, groups)

    return (datalist, params)


@do_profile()
def match_ability_json(match, split_var='No Split'):

    skill_builds = SkillBuild.objects.filter(
        player_match_summary__match__steam_id=match
    ).select_related().order_by('player_match_summary', 'level')
    if len(skill_builds) == 0:
        raise NoDataFound

    hero_classes = hero_classes_dict()

    datalist = []
    for build in skill_builds:

        side = build.player_match_summary.which_side()
        hero = build.player_match_summary.hero.name
        if split_var == 'No Split':
            split_param = 'No Split'
        elif split_var == 'hero':
            split_param = hero
        elif split_var == 'side':
            split_param = side

        datadict = datapoint_dict()
        minidict = {
            'x_var': round(build.time / 60.0, 3),
            'y_var': build.level,
            'label': hero,
            'tooltip': build.ability.name,
            'split_var': split_param,
            'group_var': hero,
            'classes': [],
        }
        datadict.update(minidict)
        if hero_classes[build.player_match_summary.hero.steam_id] is not None:
            datadict['classes'].extend(
                hero_classes[build.player_match_summary.hero.steam_id]
            )
        datadict['classes'].append(
            slugify(
                unicode(build.player_match_summary.which_side())
            )
        )

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
    params['outerWidth'] = 400
    params['outerHeight'] = 400

    return (datalist, params)


@do_profile()
def match_parameter_json(match_id, x_var, y_var):
    pmses = PlayerMatchSummary.objects.filter(match__steam_id=match_id)\
        .select_related()
    if len(pmses) == 0:
        raise NoDataFound

    hero_classes = hero_classes_dict()
    data_list, groups = [], []
    for pms in pmses:
        datadict = datapoint_dict()
        group = fetch_pms_attribute(pms, 'which_side')
        groups.append(group)
        datadict.update({
            'x_var': fetch_pms_attribute(pms, x_var),
            'y_var': fetch_pms_attribute(pms, y_var),
            'group_var': group,
            'split_var': '{x} vs {y}'.format(x=x_var, y=y_var),
            'label': fetch_pms_attribute(pms, 'hero_name'),
            'tooltip': fetch_pms_attribute(pms, 'hero_name'),
            'classes': [],
        })
        if hero_classes[pms.hero.steam_id] is not None:
            datadict['classes'].extend(hero_classes[pms.hero.steam_id])
        datadict['classes'].append(slugify(unicode(pms.which_side())))

        data_list.append(datadict)

    params = params_dict()
    params['x_min'] = min([d['x_var'] for d in data_list])
    params['x_max'] = max([d['x_var'] for d in data_list])
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = max([d['y_var'] for d in data_list])
    params['x_label'] = fetch_attribute_label(x_var)
    params['y_label'] = fetch_attribute_label(y_var)
    if params['y_min'] > 1000:
        params['y_label'] += ' (K)'
        for d in data_list:
            d['y_var'] /= 1000.0
        params['y_max'] = int(floor(round(params['y_max']/1000.0, 0)))
        params['y_min'] = int(floor(round(params['y_min']/1000.0, 0)))
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 12*len(str(params['y_max']))

    params['outerWidth'] = 250
    params['outerHeight'] = 250
    params = color_scale_params(params, groups)

    return (data_list, params)


@do_profile()
def single_match_parameter_json(match, y_var, title):
    pmses = PlayerMatchSummary.objects.filter(match__steam_id=match)\
        .select_related()
    if len(pmses) == 0:
        raise NoDataFound

    hero_classes = hero_classes_dict()
    data_list = []
    for pms in pmses:
        datadict = datapoint_dict()
        group = fetch_pms_attribute(pms, 'which_side')
        datadict.update({
            'x_var': pms.hero.safe_name(),
            'y_var': fetch_pms_attribute(pms, y_var),
            'group_var': group,
            'split_var': title,
            'label': pms.hero.safe_name(),
            'tooltip': pms.hero.safe_name(),
            'classes': [],
        })
        if hero_classes[pms.hero.steam_id] is not None:
            datadict['classes'].extend(hero_classes[pms.hero.steam_id])
        datadict['classes'].append(slugify(unicode(pms.which_side())))
        data_list.append(datadict)

    params = params_dict()
    params['x_set'] = [d['x_var'] for d in data_list]
    params['y_min'] = min([d['y_var'] for d in data_list])
    params['y_max'] = max([d['y_var'] for d in data_list])
    params['x_label'] = 'Hero'
    params['y_label'] = fetch_attribute_label(y_var)
    params['legendWidthPercent'] = .8
    params['legendHeightPercent'] = .05

    params['padding']['bottom'] = 90
    params['margin']['left'] = 45

    if params['y_max'] > 1000:
        params['y_label'] += ' (K)'
        for d in data_list:
            d['y_var'] /= 1000.0
        params['y_max'] = int(floor(round(params['y_max']/1000.0, 0)))
        params['y_min'] = int(floor(round(params['y_min']/1000.0, 0)))
    params['chart'] = 'barplot'
    params['outerHeight'] = 250
    params = color_scale_params(params, [d['group_var'] for d in data_list])

    return (data_list, params)


@do_profile()
def match_role_json(match):
    pmses = PlayerMatchSummary.objects.filter(match__steam_id=match)
    if len(pmses) == 0:
        raise NoDataFound

    dire_annotations = PlayerMatchSummary.objects.filter(
        match__steam_id=match,
        player_slot__gte=6).values(
        'hero__assignment__role__name'
        ).annotate(Sum('hero__assignment__magnitude')).order_by()

    radiant_annotations = PlayerMatchSummary.objects.filter(
        match__steam_id=match,
        player_slot__lte=6).values(
        'hero__assignment__role__name'
        ).annotate(Sum('hero__assignment__magnitude')).order_by()

    dire_roles = {
        d['hero__assignment__role__name']:
        d['hero__assignment__magnitude__sum']
        for d in dire_annotations
        }

    radiant_roles = {
        d['hero__assignment__role__name']:
        d['hero__assignment__magnitude__sum']
        for d in radiant_annotations
        }

    role_set = set(chain(radiant_roles.iterkeys(), dire_roles.iterkeys()))
    data_list = []
    for role in role_set:
        if role is not None:
            datadict = datapoint_dict()
            datadict.update({
                'x_var': radiant_roles.get(role, 0),
                'y_var': dire_roles.get(role, 0),
                'group_var': role,
                'split_var': 'Role Breakdown',
                'label': role,
                'tooltip': role,
                'classes': [slugify(role)],
            })
            data_list.append(datadict)

    params = params_dict()
    xmax = max([d['x_var'] for d in data_list])
    ymax = max([d['y_var'] for d in data_list])
    absmax = max(xmax, ymax)
    params['x_min'] = 0
    params['x_max'] = absmax
    params['y_min'] = 0
    params['y_max'] = absmax
    params['x_label'] = 'Radiant Role Magnitude'
    params['y_label'] = 'Dire Role Magnitude'
    params['draw_path'] = False
    params['chart'] = 'xyplot'
    params['margin']['left'] = 30
    params['outerWidth'] = 250
    params['outerHeight'] = 250
    params = color_scale_params(params, [d['group_var'] for d in data_list])
    return (data_list, params)


@do_profile()
def match_list_json(match_list, player_list):
    pmses = PlayerMatchSummary.objects.filter(
        match__steam_id__in=match_list,
        player__steam_id__in=player_list,
    )

    if len(pmses) == 0:
        raise NoDataFound

    sbs = SkillBuild.objects.filter(
        player_match_summary__in=pmses,
    ).select_related().order_by('player_match_summary', 'level')
    sbs = sbs.values(
        'level',
        'time',
        'player_match_summary__is_win',
        'player_match_summary__id',
        'player_match_summary__match__skill',
        'player_match_summary__match__steam_id',
        'player_match_summary__player__persona_name',
    )
    datalist, xs, ys, groups = [], [], [], []

    for build in sbs:
        if build['level'] == 1:
            subtractor = build['time']/60.0

        datapoint = datapoint_dict()
        datapoint['x_var'] = round(build['time']/60.0-subtractor, 3)
        xs.append(round(build['time']/60.0-subtractor, 3))
        datapoint['y_var'] = build['level']
        ys.append(build['level'])

        group = "{match}, {name}".format(
            match=build['player_match_summary__match__steam_id'],
            name=build['player_match_summary__player__persona_name'],
        )

        datapoint['group_var'] = group
        groups.append(group)

        datapoint['series_var'] = group

        datapoint['label'] = build[
            'player_match_summary__player__persona_name'
        ]
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
    params = color_scale_params(params, groups)

    return (datalist, params)
