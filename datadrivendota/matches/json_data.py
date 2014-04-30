from math import floor
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Sum
from django.core.urlresolvers import reverse
from itertools import chain
from matches.models import (
    PlayerMatchSummary,
    Match,
    fetch_attribute_label,
    fetch_pms_attribute,
    SkillBuild
)
from utils.exceptions import NoDataFound
from utils.charts import (
    hero_classes_dict,
    XYPlot, DataPoint, BarPlot, TasselPlot,
    valid_var
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
        panel_var,
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

    c = XYPlot()
    for player in players:

        player_obj = Player.objects.get(steam_id=player)
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

        for i, annotation in enumerate(chain(
            radiant_annotations,
            dire_annotations
        )):
            d = DataPoint()
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

            if not valid_var(panel_var):
                pass
            elif panel_var == 'game_mode':
                split_param = annotation.game_mode.description
            elif panel_var == 'player':
                split_param = player_obj.display_name
            elif panel_var == 'is_win':
                if mapping_dict[annotation.steam_id]['is_win']:
                    split_param = 'Won'
                else:
                    split_param = 'Lost'

            if not valid_var(group_var):
                group_param = None
                pass
            elif group_var == 'game_mode':
                group_param = annotation.game_mode.description
            elif group_var == 'player':
                group_param = player_obj.display_name
            elif group_var == 'is_win':
                if mapping_dict[annotation.steam_id]['is_win']:
                    group_param = 'Won'
                else:
                    group_param = 'Lost'
            else:
                print group_var
            d.x_var = plot_x_var
            d.y_var = plot_y_var
            d.label = annotation.steam_id
            d.tooltip = annotation.steam_id
            d.panel_var = split_param
            d.group_var = group_param
            d.url = 'matches/{0}'.format(annotation.steam_id)
            if hero_classes[
                    mapping_dict[annotation.steam_id]['hero_id']
            ] is not None:
                d.classes.extend(
                    hero_classes[
                        mapping_dict[annotation.steam_id]['hero_id']
                        ]
                )

            c.datalist.append(d)
    if len(c.datalist) == 0:
        raise NoDataFound

    c.params.legendWidthPercent = .25
    if x_var == 'duration':
        c.params.x_label = 'Duration (m)'
    else:
        c.params.x_label = x_var.title()
    c.params.y_label = y_var.title()
    return c


@do_profile()
def player_endgame_json(
        players,
        game_modes,
        x_var,
        y_var,
        panel_var,
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

    c = XYPlot()
    for pms in selected_summaries:
        d = DataPoint()
        d.x_var = fetch_pms_attribute(pms, x_var)
        d.y_var = fetch_pms_attribute(pms, y_var)
        d.label = fetch_pms_attribute(pms, group_var)
        d.tooltip = fetch_pms_attribute(pms, 'match_id')
        d.url = reverse(
            'matches:match_detail',
            kwargs={'match_id': fetch_pms_attribute(pms, 'match_id')}
        )
        if valid_var(group_var):
            d.group_var = fetch_pms_attribute(pms, group_var)
        if valid_var(panel_var):
            d.panel_var = fetch_pms_attribute(pms, panel_var)
        if hero_classes[pms.hero.steam_id] is not None:
            d.classes.extend(
                hero_classes[pms.hero.steam_id]
            )

        c.datalist.append(d)

    c.params.x_label = x_var.title()
    c.params.y_label = y_var.title()
    return c


@do_profile()
def team_endgame_json(
        players,
        game_modes,
        x_var,
        y_var,
        panel_var,
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
        c = XYPlot()
        for annotation in chain(radiant_annotations, dire_annotations):
            match_id = annotation.steam_id

            d = DataPoint()

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

            d.x_var = plot_x_var
            d.y_var = plot_y_var
            d.label = match_id
            d.tooltip = match_id
            d.url = reverse(
                'matches:match_detail',
                kwargs={'match_id': match_id}
            )

            c.datalist.append(d)
            xlab = fetch_attribute_label(attribute=x_var)
            ylab = fetch_attribute_label(attribute=y_var)
    except AttributeError:
        raise NoDataFound
    c.params.x_label = xlab
    c.params.y_label = ylab

    return c


@do_profile()
def match_ability_json(match, panel_var=None):

    skill_builds = SkillBuild.objects.filter(
        player_match_summary__match__steam_id=match
    ).select_related().order_by('player_match_summary', 'level')
    if len(skill_builds) == 0:
        raise NoDataFound

    hero_classes = hero_classes_dict()

    c = XYPlot()
    for build in skill_builds:

        side = build.player_match_summary.which_side()
        hero = build.player_match_summary.hero.name
        if not valid_var(panel_var):
            split_param = None
            pass
        elif panel_var == 'hero':
            split_param = hero
        elif panel_var == 'side':
            split_param = side

        d = DataPoint()
        d.x_var = round(build.time / 60.0, 3),
        d.y_var = build.level
        d.label = hero
        d.tooltip = build.ability.name
        d.panel_var = split_param
        d.group_var = hero

        if hero_classes[build.player_match_summary.hero.steam_id] is not None:
            d.classes.extend(
                hero_classes[build.player_match_summary.hero.steam_id]
            )
        d.classes.append(
            slugify(
                unicode(build.player_match_summary.which_side())
            )
        )

        c.datalist.append(d)

    c.params.x_label = 'Time (m)'
    c.params.y_label = 'Level'
    c.params.draw_path = True
    c.params.outerWidth = 400
    c.params.outerHeight = 400

    return c


@do_profile()
def match_parameter_json(match_id, x_var, y_var):
    pmses = PlayerMatchSummary.objects.filter(match__steam_id=match_id)\
        .select_related()
    if len(pmses) == 0:
        raise NoDataFound

    hero_classes = hero_classes_dict()
    c = XYPlot()
    for pms in pmses:
        d = DataPoint()
        group = fetch_pms_attribute(pms, 'which_side')
        d.x_var = fetch_pms_attribute(pms, x_var)
        d.y_var = fetch_pms_attribute(pms, y_var)
        d.group_var = group
        d.panel_var = '{x} vs {y}'.format(x=x_var, y=y_var)
        d.label = fetch_pms_attribute(pms, 'hero_name')
        d.tooltip = fetch_pms_attribute(pms, 'hero_name')
        d.classes = []
        if hero_classes[pms.hero.steam_id] is not None:
            d.classes.extend(hero_classes[pms.hero.steam_id])
        d.classes.append(slugify(unicode(pms.which_side())))

        c.datalist.append(d)

    c.params.x_label = fetch_attribute_label(x_var)
    c.params.y_label = fetch_attribute_label(y_var)
    if c.params.y_min > 1000:
        c.params.y_label += ' (K)'
        for d in c.data_list:
            d.y_var /= 1000.0
        c.params.y_max = int(floor(round(c.params.y_max/1000.0, 0)))
        c.params.y_min = int(floor(round(c.params.y_min/1000.0, 0)))
    c.params.draw_path = False

    c.params.outerWidth = 250
    c.params.outerHeight = 250

    return c


@do_profile()
def single_match_parameter_json(match, y_var):
    pmses = PlayerMatchSummary.objects.filter(match__steam_id=match)\
        .select_related()
    if len(pmses) == 0:
        raise NoDataFound

    hero_classes = hero_classes_dict()
    c = BarPlot()
    for pms in pmses:
        d = DataPoint()
        group = fetch_pms_attribute(pms, 'which_side')
        d.x_var = pms.hero.safe_name()
        d.y_var = fetch_pms_attribute(pms, y_var)
        d.group_var = group
        d.label = pms.hero.safe_name()
        d.tooltip = pms.hero.safe_name()
        if hero_classes[pms.hero.steam_id] is not None:
            d.classes.extend(hero_classes[pms.hero.steam_id])
            d.classes.append(slugify(unicode(pms.which_side())))
        c.datalist.append(d)

    c.params.x_label = 'Hero'
    c.params.y_label = fetch_attribute_label(y_var)
    c.params.legendWidthPercent = .8
    c.params.legendHeightPercent = .05

    c.params.padding['bottom'] = 90
    c.params.margin['left'] = 45

    if c.params.y_max > 1000:
        c.params.y_label += ' (K)'
        for d in c.data_list:
            d.y_var /= 1000.0
        c.params.y_max = int(floor(round(c.params.y_max/1000.0, 0)))
        c.params.y_min = int(floor(round(c.params.y_min/1000.0, 0)))
    c.params.outerHeight = 250
    return c


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
    c = XYPlot()
    for role in role_set:
        if role is not None:
            d = DataPoint()
            d.x_var = radiant_roles.get(role, 0)
            d.y_var = dire_roles.get(role, 0)
            d.group_var = role
            d.panel_var = 'Role Breakdown'
            d.label = role
            d.tooltip = role
            d.classes = [slugify(role)]
            c.datalist.append(d)

    xmax = max([d.x_var for d in c.datalist])
    ymax = max([d.y_var for d in c.datalist])
    absmax = max(xmax, ymax)
    c.params.x_min = 0
    c.params.x_max = absmax
    c.params.y_min = 0
    c.params.y_max = absmax
    c.params.x_label = 'Radiant Role Magnitude'
    c.params.y_label = 'Dire Role Magnitude'
    c.params.margin['left'] = 30
    c.params.outerWidth = 250
    c.params.outerHeight = 250
    return c


@do_profile()
def match_list_json(matches, player_list):
    pmses = PlayerMatchSummary.objects.filter(
        match__steam_id__in=matches,
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

    c = TasselPlot()
    for build in sbs:
        if build['level'] == 1:
            subtractor = build['time']/60.0

        d = DataPoint()
        d.x_var = round(build['time']/60.0-subtractor, 3)
        d.y_var = build['level']

        group = "{match}, {name}".format(
            match=build['player_match_summary__match__steam_id'],
            name=build['player_match_summary__player__persona_name'],
        )

        d.group_var = group
        d.series_var = group

        d.label = build[
            'player_match_summary__player__persona_name'
        ]
        d.panel_var = 'Skill Progression'
        c.datalist.append(d)

    c.params.x_min = 0
    c.params.x_label = 'Time (m)'
    c.params.y_label = 'Level'

    return c
