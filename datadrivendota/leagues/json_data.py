import datetime
from django.conf import settings
from django.db.models import Count
from matches.models import PlayerMatchSummary, Match, PickBan
from .models import League
from utils.exceptions import NoDataFound
from utils.charts import (
    hero_classes_dict,
    XYPlot,
    DataPoint,
)
from heroes.models import Hero
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
def league_winrate_json(
        league,
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

    try:
        league = League.objects.get(steam_id=league)
    except League.DoesNotExist:
        raise NoDataFound

    annotations = PlayerMatchSummary.objects.filter(
        match__validity=Match.LEGIT,
        match__start_time__gte=min_date_utc,
        match__start_time__lte=max_date_utc,
    )

    annotations = annotations.filter(
        match__league=league
        )
    annotations = annotations.values('hero__name', 'is_win')\
        .annotate(Count('is_win'))

    if len(annotations) == 0:
        raise NoDataFound

    heroes = list(set([
        row['hero__name'] for row in annotations if row['hero__name'] != ''
        ]))
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

    c = XYPlot()
    for hero in heroes:
        if group_var == 'hero':
            group = hero_info_dict[hero]['name']
        elif group_var == 'alignment':
            group = hero_info_dict[hero]['alignment'].title()

        url_str = ''

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
def league_pick_ban_json(
        league,
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

    try:
        league = League.objects.get(steam_id=league)

    except League.DoesNotExist:
        raise NoDataFound

    matches = Match.objects.filter(
        validity=Match.LEGIT,
        start_time__gte=min_date_utc,
        start_time__lte=max_date_utc,
    )

    matches = matches.filter(
        league=league
        ).values('steam_id')

    if len(matches) == 0:
        raise NoDataFound

    pbs = PickBan.objects.filter(
        match__steam_id__in=matches
        ).values(
        'hero', 'is_pick', 'hero__name', 'hero__steam_id',
        'hero__herodossier__alignment'
        ).annotate(
        Count('is_pick')
        ).order_by()

    if len(pbs) == 0:
        raise NoDataFound

    hero_classes = hero_classes_dict()
    heroes = {
        h.name: h.herodossier.alignment.title()
        for h in Hero.objects.filter(visible=True).select_related()
        }

    annotations = {}
    for pb in pbs:
        if pb['hero__steam_id'] not in annotations:
            annotations[pb['hero__steam_id']] = {
                'picks': 0,
                'bans': 0,
                'hero__name': pb['hero__name'],
                'hero__steam_id': pb['hero__steam_id'],
                'alignment': pb['hero__herodossier__alignment'],
            }

        if pb['is_pick'] is True:
            annotations[pb['hero__steam_id']]['picks'] = pb['is_pick__count']
        elif pb['is_pick'] is False:
            annotations[pb['hero__steam_id']]['bans'] = pb['is_pick__count']

    c = XYPlot()
    for annotation in annotations.itervalues():
        if group_var == 'hero':
            group = annotation['hero__name']
        elif group_var == 'alignment':
            group = annotation['alignment'].title()

        url_str = ''

        d = DataPoint()

        d.x_var = annotation['picks']
        d.y_var = annotation['bans']
        d.group_var = group
        d.url = url_str
        d.label = annotation['hero__name']
        d.tooltip = annotation['hero__name']
        d.classes = []
        if hero_classes[annotation['hero__steam_id']] is not None:
            d.classes.extend(
                hero_classes[annotation['hero__steam_id']]
            )

        c.datalist.append(d)

    if group_var != 'alignment':
        c.params.draw_legend = False

    c.params.y_min = 0
    c.params.x_min = 0
    c.params.x_label = 'Picks'
    c.params.y_label = 'Bans'
    c.params.draw_path = False
    c.params.margin['left'] = 24
    c.params.outerWidth = 300
    c.params.outerHeight = 300
    c.params.legendWidthPercent = .7
    c.params.legendHeightPercent = .7
    return c
