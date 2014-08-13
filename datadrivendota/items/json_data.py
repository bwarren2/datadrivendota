from matches.models import (
    PlayerMatchSummary,
)
from utils.exceptions import NoDataFound
from utils.charts import XYPlot, DataPoint
from matches.models import GameMode


def item_endgame(
    hero=None,
    player=None,
    skill_level=None,
    game_modes=[],
):
    if game_modes == []:
        game_modes = [
            mode.steam_id
            for mode in GameMode.objects.filter(is_competitive=True)
        ]

    if hero is None and player is None:
        raise NoDataFound

    pmses = PlayerMatchSummary.objects.all()

    if hero is not None:
        pmses = pmses.filter(hero__steam_id=hero)
    if player is not None:
        pmses = pmses.filter(player__steam_id=player)
    if skill_level is not None and skill_level != '':
        pmses = pmses.filter(match__skill=skill_level)

    itemDict = {}
    pmses = pmses.select_related(
        'item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5', 'match'
        )[:500]
    for p in pmses:
        for attr in [
            'item_0',
            'item_1',
            'item_2',
            'item_3',
            'item_4',
            'item_5'
        ]:
            itm = getattr(p, attr)
            if itm not in itemDict:
                itemDict[itm] = {
                    'wins': set(),
                    'losses': set(),
                }
            if p.is_win:
                itemDict[itm]['wins'].add(p.match.steam_id)
            else:
                itemDict[itm]['losses'].add(p.match.steam_id)

    chart = XYPlot()
    for itm in itemDict:
        itemDict[itm]['games'] = \
            len(itemDict[itm]['losses']) + len(itemDict[itm]['wins'])
        denominator = 1 if itemDict[itm]['games'] == 0 \
            else itemDict[itm]['games']
        itemDict[itm]['winrate'] = len(itemDict[itm]['wins'])\
            / float(denominator) * 100

        d = DataPoint()
        d.x_var = itemDict[itm]['games']
        d.y_var = itemDict[itm]['winrate']
        d.label = itm.name
        d.tooltip = itm.name
        d.panel_var = ''
        d.group_var = ''
        d.point_size = itm.cost
        chart.datalist.append(d)

    if len(chart.datalist) == 0:
        raise NoDataFound

    chart.params.x_min = 0
    chart.params.y_min = 0
    chart.params.y_max = 100
    chart.params.legendWidthPercent = .25
    chart.params.x_label = 'Games'
    chart.params.y_label = 'Winrate'
    chart.params.margin['left'] = 24
    chart.params.pointDomainMin = 0
    chart.params.pointDomainMax = 5000
    chart.params.pointSizeMin = 2
    chart.params.pointSizeMax = 5
    return chart
