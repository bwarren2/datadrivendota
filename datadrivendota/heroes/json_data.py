import operator
from itertools import chain

from django.conf import settings
from django.core.urlresolvers import reverse

from heroes.models import HeroDossier, Hero, invalid_option, Ability
from matches.models import (
    PlayerMatchSummary,
    Match,
    fetch_match_attributes,
    SkillBuild,
    skill_name,
    fetch_pms_attribute,
    GameMode,
    fetch_attribute_label,
)
from players.models import Player
from django.db.models import Count

from utils.exceptions import NoDataFound
from utils.charts import (
    hero_classes_dict,
    DataPoint,
    XYPlot, BarPlot, TasselPlot, TasselDataPoint,
    valid_panel_var
    )

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
def hero_vitals_json(heroes, stats):
    selected_hero_dossiers = HeroDossier.objects.filter(
        hero__steam_id__in=heroes
    )

    if len(selected_hero_dossiers) == 0 or invalid_option(stats):
        raise NoDataFound

    hero_classes = hero_classes_dict()
    c = XYPlot()
    for hero_dossier in selected_hero_dossiers:
        for stat in stats:
            for level in range(1, 26):
                d = DataPoint()
                d.x_var = level
                d.y_var = hero_dossier.level_stat(stat, level)
                d.group_var = hero_dossier.hero.name
                d.label = hero_dossier.hero.name
                d.tooltip = "{hero}, {val}".format(
                    hero=hero_dossier.hero.name,
                    val=hero_dossier.level_stat(stat, level)
                )
                d.panel_var = stat.title()

                if hero_classes[hero_dossier.hero.steam_id] is not None:
                    d.classes.extend(
                        hero_classes[hero_dossier.hero.steam_id]
                    )

                c.datalist.append(d)
    c.params.x_label = 'Level'
    c.params.y_label = 'Quantity'
    c.params.draw_path = True
    c.params.outerWidth = 300
    c.params.outerHeight = 300
    return c


@do_profile()
def hero_lineup_json(heroes, stat, level):

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

    hero_value = sorted(
        hero_value.iteritems(),
        key=operator.itemgetter(1),
        reverse=True
    )

    hero_classes = hero_classes_dict()
    c = BarPlot()
    xs = []
    for key, val in hero_value:

        d = DataPoint()
        group = key.hero.safe_name() \
            if key.hero.safe_name() in selected_names \
            else key.alignment.title()
        xs.append(key.hero.safe_name())
        d.x_var = key.hero.safe_name()
        d.y_var = val
        d.label = key.hero.safe_name()
        d.tooltip = "{name} ({val})".format(
            name=key.hero.safe_name(),
            val=val,
        )
        d.group_var = group
        d.classes = []
        d.panel_var = 'Hero {stat}'.format(stat=stat)

        if hero_classes[key.hero.steam_id] is not None:
            d.classes.extend(
                hero_classes[key.hero.steam_id]
            )

        c.datalist.append(d)

    c.params.y_min = 0
    c.params.x_label = 'Hero'
    c.params.y_label = stat
    c.params.outerWidth = 800
    c.params.outerHeight = 500
    c.params.legendWidthPercent = .7
    c.params.legendHeightPercent = .8
    c.params.padding['bottom'] = 120
    c.params.tick_values = [x for ind, x in enumerate(xs) if ind % 2 == 0]
    return c


@do_profile()
def hero_performance_chart_json(
    hero,
    player,
    x_var,
    y_var,
    group_var,
    panel_var,
    game_modes=None,
):
    if game_modes is None:
        game_modes = [
            mode.steam_id
            for mode in GameMode.objects.filter(is_competitive=True)
        ]

    #Make an iterable of data
    superset_pmses = PlayerMatchSummary.objects.filter(
        match__game_mode__steam_id__in=game_modes,
        hero__steam_id=hero,
        match__validity=Match.LEGIT
    )
    skill1 = superset_pmses.filter(match__skill=1)\
        .order_by('-match__start_time').select_related()[:100]
    skill2 = superset_pmses.filter(match__skill=2)\
        .order_by('-match__start_time').select_related()[:100]
    skill3 = superset_pmses.filter(match__skill=3)\
        .order_by('-match__start_time').select_related()[:100]

    if player is not None:
        player_games = superset_pmses.filter(
            player__steam_id=player
        ).select_related()
        pms_pool = list(chain(skill1, skill2, skill3, player_games))
        player_game_ids = fetch_match_attributes(player_games, 'match_id')[0]
    else:
        pms_pool = list(chain(skill1, skill2, skill3))
        player_game_ids = []

    if len(pms_pool) == 0:
        raise NoDataFound

    matching = PlayerMatchSummary.objects.filter(
        id__in=[p.id for p in pms_pool]
        ).values('match__steam_id', 'id')

    match_dict = {d['id']: d['match__steam_id'] for d in matching}

    #Iterate through it, making data points for the chart
    try:
        hero_classes = hero_classes_dict()
        c = XYPlot()
        for pms in pms_pool:
            d = DataPoint()
            d.x_var = fetch_pms_attribute(pms, x_var)
            d.y_var = fetch_pms_attribute(pms, y_var)
            d.label = match_dict[pms.id]
            d.tooltip = match_dict[pms.id]
            d.url = '/matches/'+str(match_dict[pms.id])
            if hero_classes[pms.hero.steam_id] is not None:
                d.classes.extend(
                    hero_classes[pms.hero.steam_id]
                )

            #Ajax API requests can't send None over the wire
            if valid_panel_var(group_var):
                if group_var == 'skill_name'\
                        and pms.match.steam_id in player_game_ids:
                            d.group_var = 'Player'
                else:
                    d.group_var = fetch_pms_attribute(pms, group_var)

            if valid_panel_var(panel_var):
                d.panel_var = fetch_pms_attribute(pms, panel_var)
            else:
                d.panel_var = "{y} vs {x}".format(
                    y=fetch_attribute_label(y_var),
                    x=fetch_attribute_label(x_var),
                )
            c.datalist.append(d)

    except AttributeError:
        raise NoDataFound

    c.params.x_label = fetch_attribute_label(x_var)
    c.params.y_label = fetch_attribute_label(y_var)
    if group_var == 'skill_name':
        c.groups = ['Low Skill', 'Medium Skill', 'High Skill']
    if player is not None and c.groups is not None:
        c.groups.append('Player')
    return c


@do_profile()
def hero_progression_json(hero, player, division, game_modes=None):
    if game_modes == [] or game_modes is None:
        game_modes = [
            mode.steam_id
            for mode in GameMode.objects.filter(is_competitive=True)
        ]

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
    hero_classes = hero_classes_dict()

    c = TasselPlot()
    for build in sbs:
        if build['level'] == 1:
            subtractor = build['time']/60.0

        d = TasselDataPoint()
        d.x_var = round(build['time']/60.0-subtractor, 3)
        d.y_var = build['level']

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

        d.group_var = group

        d.series_var = build[
            'player_match_summary__match__steam_id'
        ]
        d.label = build[
            'player_match_summary__player__persona_name'
        ]
        d.panel_var = 'Skill Progression'
        hero_id = build['player_match_summary__hero__steam_id']
        if hero_classes[hero_id] is not None:
            d.classes.extend(
                hero_classes[hero_id]
            )

        c.datalist.append(d)

    c.params.x_min = 0
    c.params.x_label = 'Time (m)'
    c.params.y_label = 'Level'

    return c


@do_profile()
def hero_skillbuild_winrate_json(
    hero,
    player,
    game_modes,
    levels,
):
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
    c = XYPlot()
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
            d = DataPoint()

            d.x_var = datadict['games']
            d.y_var = datadict['winrate']
            d.group_var = "By Level {lvl}".format(lvl=level)
            d.label = to_label(build)
            d.tooltip = to_label(build)
            c.datalist.append(d)

    c.params.x_min = 0
    c.params.y_min = 0
    c.params.y_max = 100
    c.params.x_label = 'Games'
    c.params.y_label = 'Winrate'
    return c


@do_profile()
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

    c = XYPlot()
    for p, info in dict_games.iteritems():

        url_str = reverse(
            'players:hero_style',
            kwargs={
                'hero_name': hero_obj.machine_name,
                'player_id': p.steam_id,
            }
        )

        d = DataPoint()
        d.x_var = info['games']
        d.y_var = info['wins']/float(info['games'])*100
        d.group_var = 'Pro' if p.pro_name is not None else 'Player'
        d.label = p.display_name
        d.tooltip = p.display_name
        d.url = url_str
        d.panel_var = 'Tracked Player Winrate'
        c.datalist.append(d)

    c.params.x_min = 0
    c.params.y_min = 0
    c.params.y_max = 100
    c.params.x_label = 'Games'
    c.params.y_label = 'Winrate'

    return c
